#!/usr/bin/env python
"""Live operator screen: phone stream -> fixture align -> AI -> PASS / CHECK / FAIL.

    python scripts/hmi.py --source http://192.168.1.23:8080/video    # MJPEG from the phone
    python scripts/hmi.py --source rtsp://192.168.1.23:8554/live     # RTSP from the phone
    python scripts/hmi.py --source 0                                 # laptop webcam
    python scripts/hmi.py --source photo.jpg                         # one still
    python scripts/hmi.py --source folder/ --headless                # batch, no window
    python scripts/hmi.py --source dataset/crops/D12/wrong --cropped # review saved crops

Keys:  q quit    s save the current frame and decision    space freeze/unfreeze

This stands in for the PLC and HMI of the industrial phase. The decision shown
is the same function used in evaluation, reading the same thresholds file, so
the demo cannot disagree with the report.
"""
import argparse
import csv
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

import _boot  # noqa: F401
from polarity import align as A
from polarity import config as C
from polarity import data
from polarity import model as M
from polarity import pipeline, quality

COLOURS = {                     # BGR
    M.PASS: (72, 160, 72),
    M.CHECK: (0, 165, 240),
    M.FAIL: (54, 54, 214),
    "NO BOARD": (110, 110, 110),
}
VIEW_W, VIEW_H = 900, 675
PANEL_W = 460


def draw_panel(cfg, decision, probability, result, fps, smoothing, thresholds, counters):
    panel = np.full((VIEW_H, PANEL_W, 3), (34, 30, 26), np.uint8)

    def text(y, s, scale=0.72, colour=(205, 205, 205), thick=2):
        cv2.putText(panel, s, (28, y), cv2.FONT_HERSHEY_SIMPLEX, scale, colour, thick,
                    cv2.LINE_AA)

    text(58, "POLARITY AI", 1.25, (245, 245, 245), 3)
    cv2.line(panel, (28, 78), (PANEL_W - 28, 78), (80, 75, 70), 2)

    text(126, f"Component   {cfg['component']}")
    text(160, f"Expected    {cfg['expected']}")
    if probability is None:
        text(194, "AI wrong    --", 0.72, (150, 150, 150))
    else:
        text(194, f"AI wrong    {probability * 100:5.1f}%", 0.78,
             COLOURS[decision], 2)

    cv2.rectangle(panel, (28, 236), (PANEL_W - 28, 344), COLOURS[decision], -1)
    size, _ = cv2.getTextSize(decision, cv2.FONT_HERSHEY_SIMPLEX, 1.8, 4)
    cv2.putText(panel, decision, (PANEL_W // 2 - size[0] // 2, 290 + size[1] // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 4, cv2.LINE_AA)

    note = {M.PASS: "polarity correct",
            M.CHECK: "uncertain — operator to confirm",
            M.FAIL: "WRONG POLARITY — stop this board",
            "NO BOARD": result.reason or "waiting for the fixture"}[decision]
    cv2.putText(panel, note[:44], (28, 378), cv2.FONT_HERSHEY_SIMPLEX, 0.58,
                (190, 190, 190), 1, cv2.LINE_AA)

    y = 436
    cv2.line(panel, (28, y - 26), (PANEL_W - 28, y - 26), (80, 75, 70), 1)
    for line in (
        f"FAIL >= {thresholds[0]:.3f}   CHECK >= {thresholds[1]:.3f}",
        f"markers {result.n_markers}/4   "
        f"sharpness {result.metrics.get('sharpness', 0):.0f}",
        f"smoothed over {smoothing} frames   {fps:4.1f} fps",
        f"session   PASS {counters[M.PASS]}  CHECK {counters[M.CHECK]}  FAIL {counters[M.FAIL]}",
    ):
        cv2.putText(panel, line, (28, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (150, 150, 150), 1, cv2.LINE_AA)
        y += 30

    cv2.putText(panel, "q quit    s save    space freeze", (28, VIEW_H - 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, (120, 120, 120), 1, cv2.LINE_AA)
    return panel


def draw_view(cfg, result, decision, frame, cropped_mode=False):
    """Flattened board with the ROI boxed, plus the crop the model actually saw."""
    if cropped_mode:
        view = cv2.resize(frame, (VIEW_W, VIEW_H), interpolation=cv2.INTER_NEAREST)
        cv2.rectangle(view, (2, 2), (VIEW_W - 3, VIEW_H - 3), COLOURS[decision], 4)
        cv2.putText(view, "pre-cropped input (no fixture)", (24, VIEW_H - 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (235, 235, 235), 2, cv2.LINE_AA)
        return view
    if result.warped is None:
        view = cv2.resize(frame, (VIEW_W, VIEW_H))
        cv2.putText(view, "fixture not detected", (30, VIEW_H - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOURS["NO BOARD"], 2, cv2.LINE_AA)
        return view

    view = cv2.resize(result.warped, (VIEW_W, VIEW_H))
    sx, sy = VIEW_W / cfg["canonical_width"], VIEW_H / cfg["canonical_height"]
    roi = cfg["roi"]
    p1 = (int(roi["x"] * sx), int(roi["y"] * sy))
    p2 = (int((roi["x"] + roi["w"]) * sx), int((roi["y"] + roi["h"]) * sy))
    cv2.rectangle(view, p1, p2, COLOURS[decision], 3)
    cv2.putText(view, f"ROI {cfg['component']}", (p1[0], max(p1[1] - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOURS[decision], 2, cv2.LINE_AA)

    if result.crop is not None:
        thumb = cv2.resize(result.crop, (200, 200))
        view[12:212, VIEW_W - 212:VIEW_W - 12] = thumb
        cv2.rectangle(view, (VIEW_W - 212, 12), (VIEW_W - 12, 212), (230, 230, 230), 2)
        cv2.rectangle(view, (VIEW_W - 212, 212), (VIEW_W - 12, 240), (30, 30, 30), -1)
        cv2.putText(view, "model input", (VIEW_W - 204, 232),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (235, 235, 235), 1, cv2.LINE_AA)
    return view


def open_source(source):
    """Return ('still', image) | ('folder', paths) | ('stream', VideoCapture)."""
    if source.isdigit():
        return "stream", cv2.VideoCapture(int(source))
    if source.startswith(("http://", "https://", "rtsp://", "udp://")):
        return "stream", cv2.VideoCapture(source)
    path = Path(source)
    if path.is_dir():
        return "folder", data.list_images(path)
    image = cv2.imread(str(path))
    if image is None:
        raise SystemExit(f"cannot read {source}")
    return "still", image


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_arg(ap)
    ap.add_argument("--source", required=True)
    ap.add_argument("--smooth", type=int, default=5,
                    help="median over this many frames; stops the verdict flickering")
    ap.add_argument("--headless", action="store_true", help="no window, write images instead")
    ap.add_argument("--save-all", action="store_true", help="save every decision, not just FAIL")
    ap.add_argument("--cropped", action="store_true",
                    help="the source already holds ROI crops, so skip fixture alignment. "
                         "Use this to replay dataset/crops or dataset/split folders.")
    args = ap.parse_args()

    cfg = C.load(args.config)
    if cfg["roi"]["w"] <= 0 and not args.cropped:
        raise SystemExit("ROI not set — run: python scripts/align.py --pick")

    classifier = M.Classifier(C.model_path(cfg))
    fail_t, check_t, origin = M.load_thresholds(cfg, C.threshold_path(cfg))
    print(f"model {classifier.arch} sha {classifier.sha}")
    print(f"thresholds from {origin}: FAIL >= {fail_t}   CHECK >= {check_t}")

    detector = A.build_detector(cfg)
    kind, handle = open_source(args.source)

    out_dir = C.results_dir() / "logs" / "hmi" / datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    log_file = open(out_dir / "decisions.csv", "w", newline="")
    log = csv.writer(log_file)
    log.writerow(["time", "component", "decision", "p_wrong", "markers", "sharpness", "source"])

    recent = deque(maxlen=max(1, args.smooth))
    counters = {M.PASS: 0, M.CHECK: 0, M.FAIL: 0}
    frames = iter(handle) if kind == "folder" else None
    fps, last_time, frozen = 0.0, time.time(), False
    window = "Polarity AI — laptop HMI"

    while True:
        # ---- next frame ----------------------------------------------------
        label = args.source
        if kind == "still":
            frame = handle.copy()
        elif kind == "folder":
            path = next(frames, None)
            if path is None:
                break
            frame = cv2.imread(str(path))
            label = path.name
            if frame is None:
                continue
        else:
            if not frozen:
                ok, frame = handle.read()
                if not ok:
                    print("stream ended or could not be opened")
                    break
                last_frame = frame
            else:
                frame = last_frame.copy()

        # ---- decide --------------------------------------------------------
        if args.cropped:
            ok, reason, metrics = quality.check(frame, cfg)
            result = pipeline.FrameResult(ok=ok, reason=reason, warped=None, crop=frame,
                                          markers=list(cfg["marker_ids"]), metrics=metrics)
        else:
            result = pipeline.process(frame, cfg, detector)
        probability, decision = None, "NO BOARD"
        if result.ok:
            raw = float(classifier.p_wrong([result.crop])[0])
            recent.append(raw)
            probability = float(np.median(recent))
            decision = M.decide(probability, fail_t, check_t)
            counters[decision] += 1
        else:
            recent.clear()

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        log.writerow([stamp, cfg["component"], decision,
                      "" if probability is None else f"{probability:.4f}",
                      result.n_markers, result.metrics.get("sharpness", ""), label])
        log_file.flush()

        now = time.time()
        fps = 0.9 * fps + 0.1 / max(now - last_time, 1e-3)
        last_time = now

        screen = np.hstack([
            draw_view(cfg, result, decision, frame, args.cropped),
            draw_panel(cfg, decision, probability, result, fps, len(recent),
                       (fail_t, check_t), counters),
        ])

        # Every FAIL is kept with a timestamp: this is the evidence the gate asks for.
        if decision == M.FAIL or args.save_all or (kind != "stream" and args.headless):
            cv2.imwrite(str(out_dir / f"{stamp}_{decision}_screen.jpg"), screen)
            if result.crop is not None:
                cv2.imwrite(str(out_dir / f"{stamp}_{decision}_crop.jpg"), result.crop)

        if args.headless:
            print(f"{label:<28} {decision:<9} "
                  f"{'--' if probability is None else f'{probability:.3f}'}  {result.reason}")
            if kind == "still":
                break
            continue

        cv2.imshow(window, screen)
        wait = 0 if kind in ("still", "folder") else 1
        key = cv2.waitKey(wait) & 0xFF
        if key == ord("q"):
            break
        if key == ord(" "):
            frozen = not frozen
        if key == ord("s"):
            cv2.imwrite(str(out_dir / f"{stamp}_{decision}_saved.jpg"), screen)
            print(f"saved {stamp} {decision}")
        if kind == "still":
            break

    if kind == "stream":
        handle.release()
    if not args.headless:
        cv2.destroyAllWindows()
    log_file.close()
    total = sum(counters.values())
    print(f"\n{total} decisions   PASS {counters[M.PASS]}   "
          f"CHECK {counters[M.CHECK]}   FAIL {counters[M.FAIL]}")
    print(f"log and saved frames: {out_dir}")


if __name__ == "__main__":
    main()
