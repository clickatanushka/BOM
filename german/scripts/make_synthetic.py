#!/usr/bin/env python
"""Render fake fixture photos so the pipeline can be tested before real boards exist.

    python scripts/make_synthetic.py --boards 8 --per-board 30

This exists for one reason: the reversed boards have to come from the factory,
and that is the slowest item in the plan. Synthetic photos let you install,
wire up and rehearse the whole chain today, so that when the real boards arrive
the only new variable is the data.

Each image is a printed fixture card seen from a slightly different angle, with
a green board, silkscreen, pads, and a dark component carrying a bright polarity
band. Correct boards have the band on the right, reversed boards on the left.
The silkscreen polarity mark stays in the same place in both classes, exactly as
on a real board, so a model cannot cheat by reading the silkscreen.

Synthetic boards are written with an 'S' prefix (board_S01) and a SYNTHETIC.txt
marker file. They must never appear in a report that supports a Go decision.
"""
import argparse
import shutil

import cv2
import numpy as np

import _boot  # noqa: F401
from polarity import align as A
from polarity import config as C
from polarity import data

PHOTO_W, PHOTO_H = 2000, 1500      # stand-in for the phone's output size


def board_style(rng):
    """Per-board character: solder mask colour, board size, clutter."""
    return {
        "mask": (int(rng.integers(28, 52)), int(rng.integers(78, 120)),
                 int(rng.integers(24, 46))),
        "width": int(rng.integers(900, 1050)),
        "height": int(rng.integers(640, 760)),
        "band_width": int(rng.integers(20, 30)),
        "body_w": int(rng.integers(150, 185)),
        "body_h": int(rng.integers(78, 96)),
        "clutter_seed": int(rng.integers(0, 10_000)),
    }


def render_card(cfg, style, reversed_polarity, rng):
    """Draw the flat fixture card, component included, in canonical coordinates."""
    w, h = cfg["canonical_width"], cfg["canonical_height"]
    card = np.full((h, w, 3), 236, np.uint8)

    # ---- markers at the canonical corners ---------------------------------
    dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, cfg["aruco_dict"]))
    marker_px = 110
    for slot, marker_id in enumerate(cfg["marker_ids"]):
        cx, cy = A.canonical_marker_points(cfg)[slot].astype(int)
        tile = cv2.aruco.generateImageMarker(dictionary, int(marker_id), marker_px)
        x0, y0 = cx - marker_px // 2, cy - marker_px // 2
        card[y0 - 14:y0 + marker_px + 14, x0 - 14:x0 + marker_px + 14] = 250
        card[y0:y0 + marker_px, x0:x0 + marker_px] = cv2.cvtColor(tile, cv2.COLOR_GRAY2BGR)

    # ---- the board ---------------------------------------------------------
    bw, bh = style["width"], style["height"]
    bx = w // 2 - bw // 2 + int(rng.integers(-12, 13))     # slack inside the taped outline
    by = h // 2 - bh // 2 + int(rng.integers(-12, 13))
    bw, bh = int(bw), int(bh)
    cv2.rectangle(card, (bx, by), (bx + bw, by + bh), style["mask"], -1)
    cv2.rectangle(card, (bx, by), (bx + bw, by + bh), (20, 45, 20), 3)

    clutter = np.random.default_rng(style["clutter_seed"])
    for _ in range(18):
        px = int(clutter.integers(bx + 30, bx + bw - 90))
        py = int(clutter.integers(by + 30, by + bh - 60))
        pw, ph = int(clutter.integers(24, 70)), int(clutter.integers(16, 44))
        shade = int(clutter.integers(20, 70))
        cv2.rectangle(card, (px, py), (px + pw, py + ph), (shade, shade, shade), -1)
        cv2.rectangle(card, (px + 4, py + 4), (px + 10, py + ph - 4), (150, 150, 155), -1)

    # ---- the component under test -----------------------------------------
    cx, cy = w // 2, by + int(bh * 0.62)
    body_w, body_h = style["body_w"], style["body_h"]
    x0, y0 = cx - body_w // 2, cy - body_h // 2

    # pads first, then the body on top
    pad_w = 34
    for px in (x0 - pad_w + 6, x0 + body_w - 6):
        cv2.rectangle(card, (px, y0 + 8), (px + pad_w, y0 + body_h - 8),
                      (172, 176, 182), -1)

    # silkscreen: outline plus the polarity bar. Identical in both classes,
    # because the silkscreen is printed on the bare board before placement.
    cv2.rectangle(card, (x0 - 16, y0 - 14), (x0 + body_w + 16, y0 + body_h + 14),
                  (225, 225, 225), 2)
    cv2.line(card, (x0 + body_w + 24, y0 - 6), (x0 + body_w + 24, y0 + body_h + 6),
             (230, 230, 230), 3)

    body_shade = int(rng.integers(24, 40))
    cv2.rectangle(card, (x0, y0), (x0 + body_w, y0 + body_h),
                  (body_shade, body_shade, body_shade + 3), -1)

    band_w = style["band_width"]
    band_x = x0 + 10 if reversed_polarity else x0 + body_w - band_w - 10
    band_shade = int(rng.integers(190, 226))
    cv2.rectangle(card, (band_x, y0 + 5), (band_x + band_w, y0 + body_h - 5),
                  (band_shade, band_shade, band_shade), -1)

    roi_side = int(max(body_w, body_h) * 1.9)
    roi = {"x": int(cx - roi_side // 2), "y": int(cy - roi_side // 2),
           "w": roi_side, "h": roi_side}
    return card, roi


def photograph(card, rng):
    """Turn the flat card into something that looks like a handheld phone photo."""
    h, w = card.shape[:2]

    # The card occupies most of the frame but keeps a margin, the way it does on
    # a real stand. Without the margin, camera tilt pushes the corner markers out
    # of shot and the fixture cannot be found.
    card_scale = float(rng.uniform(0.74, 0.84))
    target_w = int(PHOTO_W * card_scale)
    target_h = int(h * target_w / w)
    flat = cv2.resize(card, (target_w, target_h))

    desk = int(rng.integers(70, 110))
    canvas = np.full((PHOTO_H, PHOTO_W, 3), (desk - 8, desk, desk + 12), np.uint8)
    x0 = (PHOTO_W - target_w) // 2 + int(rng.integers(-30, 31))
    y0 = (PHOTO_H - target_h) // 2 + int(rng.integers(-30, 31))
    x0 = max(0, min(x0, PHOTO_W - target_w))
    y0 = max(0, min(y0, PHOTO_H - target_h))
    canvas[y0:y0 + target_h, x0:x0 + target_w] = flat

    # slight off-axis phone position
    jitter = 34
    src = np.float32([[0, 0], [PHOTO_W, 0], [PHOTO_W, PHOTO_H], [0, PHOTO_H]])
    dst = src + rng.integers(-jitter, jitter + 1, src.shape).astype(np.float32)
    frame = cv2.warpPerspective(canvas, cv2.getPerspectiveTransform(src, dst),
                                (PHOTO_W, PHOTO_H), borderValue=(desk, desk, desk))
    angle = float(rng.uniform(-3.0, 3.0))
    frame = cv2.warpAffine(frame,
                           cv2.getRotationMatrix2D((PHOTO_W / 2, PHOTO_H / 2), angle, 1.0),
                           (PHOTO_W, PHOTO_H), borderValue=(desk, desk, desk))

    # one lamp off to the side, plus a gentle falloff
    yy, xx = np.mgrid[0:PHOTO_H, 0:PHOTO_W].astype(np.float32)
    lx = float(rng.uniform(0.2, 0.8)) * PHOTO_W
    ly = float(rng.uniform(0.1, 0.7)) * PHOTO_H
    distance = np.sqrt((xx - lx) ** 2 + (yy - ly) ** 2) / (PHOTO_W * 1.1)
    lighting = (1.18 - 0.40 * distance) * float(rng.uniform(0.86, 1.10))
    frame = np.clip(frame.astype(np.float32) * lighting[..., None], 0, 255)

    frame += rng.normal(0, float(rng.uniform(1.5, 4.5)), frame.shape)
    frame = np.clip(frame, 0, 255).astype(np.uint8)

    # focus varies shot to shot; some frames are soft enough that the quality
    # gate should reject them, which is the behaviour we want to exercise.
    blur = float(rng.uniform(0.0, 1.4))
    if blur > 0.35:
        k = int(blur * 3) * 2 + 1
        frame = cv2.GaussianBlur(frame, (k, k), blur)
    return frame


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_arg(ap)
    ap.add_argument("--boards", type=int, default=8, help="boards per class (default 8)")
    ap.add_argument("--per-board", type=int, default=30, help="photos per board (default 30)")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--clean", action="store_true", help="delete existing synthetic boards first")
    ap.add_argument("--set-roi", action="store_true",
                    help="write the exact component ROI into the config, "
                         "skipping the interactive picker")
    args = ap.parse_args()

    cfg = C.load(args.config)
    raw_root = C.raw_dir(cfg)

    if args.clean:
        for label in data.LABELS:
            for board in data.board_dirs(raw_root, label):
                if board.name.startswith("board_S"):
                    shutil.rmtree(board)

    print("SYNTHETIC DATA — for testing the pipeline only.")
    print("Never report gate numbers measured on these images.\n")

    roi = None
    total = 0
    for label in data.LABELS:
        reversed_polarity = label == "wrong"
        for board_index in range(1, args.boards + 1):
            board_id = f"S{board_index:02d}"
            rng = np.random.default_rng(args.seed + board_index * 100 + (7 if reversed_polarity else 0))
            style = board_style(rng)
            target = raw_root / label / f"board_{board_id}"
            target.mkdir(parents=True, exist_ok=True)
            for shot in range(1, args.per_board + 1):
                card, roi = render_card(cfg, style, reversed_polarity, rng)
                frame = photograph(card, rng)
                name = data.image_name(cfg["component"], label, board_id, shot, ".jpg")
                cv2.imwrite(str(target / name), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
                total += 1
        print(f"  {label:<8} {args.boards} boards x {args.per_board} photos")

    (raw_root / "SYNTHETIC.txt").write_text(
        "Boards named board_S* are computer generated, not photographs of real "
        "hardware.\nThey exist to exercise the pipeline before real reversed boards "
        "are available.\nDelete them before collecting the dataset that supports a "
        "Go/No-Go decision:\n\n    rm -rf dataset/raw/*/*/board_S*\n"
    )

    print(f"\nwrote {total} images to {raw_root}")
    if args.set_roi and roi:
        cfg["roi"] = roi
        C.save(cfg)
        print(f"ROI written to config: {roi}")
        print("next: python scripts/align.py")
    elif roi:
        print(f"the component sits at ROI x={roi['x']} y={roi['y']} "
              f"w={roi['w']} h={roi['h']} in canonical coordinates")
        print(f"next: python scripts/align.py --roi {roi['x']},{roi['y']},{roi['w']},{roi['h']} --pad 0")


if __name__ == "__main__":
    main()
