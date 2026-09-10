#!/usr/bin/env python
"""Flatten every raw photo against the fixture and cut the component ROI.

Set the ROI once, then batch-process:

    python scripts/align.py --pick                 # drag a box, press ENTER
    python scripts/align.py --roi 700,520,260,260  # same thing without a display
    python scripts/align.py                        # dataset/raw -> dataset/crops
    python scripts/align.py --preview              # show 12 crops as a contact sheet

Rejected photos are listed in results/logs/align.csv with the reason, so a bad
capture session shows up as a pattern instead of quietly poisoning the dataset.
"""
import argparse
import csv
from collections import Counter

import cv2
import numpy as np

import _boot  # noqa: F401
from polarity import align as A
from polarity import config as C
from polarity import data, pipeline


def pick_roi(cfg, detector, args):
    """Open the first alignable photo and let the user drag the component box."""
    candidates = [args.image] if args.image else data.list_images(C.raw_dir(cfg))
    if not candidates:
        raise SystemExit("no raw photos yet — run scripts/ingest.py first")

    for path in candidates:
        image = cv2.imread(str(path))
        if image is None:
            continue
        warped, found = A.flatten(image, cfg, detector)
        if warped is not None:
            print(f"using {path}  ({len(found)}/4 markers)")
            break
    else:
        raise SystemExit(
            "could not find the four fixture markers in any photo.\n"
            "Check: all four markers fully inside the frame, white border intact, "
            "no glare on them, printed at 100% scale."
        )

    box = cv2.selectROI("Drag a box around the component, then press ENTER",
                        warped, showCrosshair=True, fromCenter=False)
    cv2.destroyAllWindows()
    x, y, w, h = (int(v) for v in box)
    if w == 0 or h == 0:
        raise SystemExit("no box drawn — nothing saved")
    return x, y, w, h


def store_roi(cfg, x, y, w, h, pad):
    """Square up the box, add margin, clamp to the canonical image, and save."""
    side = int(max(w, h) * (1.0 + pad))
    cx, cy = x + w // 2, y + h // 2
    side = min(side, cfg["canonical_width"], cfg["canonical_height"])
    x = int(np.clip(cx - side // 2, 0, cfg["canonical_width"] - side))
    y = int(np.clip(cy - side // 2, 0, cfg["canonical_height"] - side))
    cfg["roi"] = {"x": x, "y": y, "w": side, "h": side}
    C.save(cfg)
    print(f"saved ROI x={x} y={y} {side}x{side} to {cfg['_path']}")
    print("  the ROI is square so the resize to the model input does not distort the part")
    print("next: python scripts/align.py")


def contact_sheet(cfg, limit=12):
    """Eyeball check: are the crops centred, sharp, and consistently framed?"""
    tiles = []
    for label in data.LABELS:
        for path in data.list_images(C.crops_dir(cfg) / label)[: limit // 2]:
            tile = cv2.imread(str(path))
            cv2.putText(tile, label, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (60, 220, 60) if label == "correct" else (60, 60, 240), 2)
            tiles.append(tile)
    if not tiles:
        raise SystemExit("no crops yet — run scripts/align.py first")
    cols = 6
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    size = cfg["crop_size"]
    blank = np.zeros((size, size, 3), np.uint8)
    grid = np.vstack([np.hstack(r + [blank] * (cols - len(r))) for r in rows])
    out = C.results_dir() / "reports" / f"{cfg['component']}_crops_preview.jpg"
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), grid)
    print(f"wrote {out}")
    try:
        cv2.imshow("crops — press any key to close", grid)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_arg(ap)
    ap.add_argument("--pick", action="store_true", help="interactively set the ROI")
    ap.add_argument("--roi", help="set the ROI non-interactively as x,y,w,h")
    ap.add_argument("--image", help="specific photo to use with --pick")
    ap.add_argument("--pad", type=float, default=0.15,
                    help="margin added around the picked box (default 0.15)")
    ap.add_argument("--preview", action="store_true", help="contact sheet of existing crops")
    ap.add_argument("--force", action="store_true", help="re-crop photos already done")
    args = ap.parse_args()

    cfg = C.load(args.config)
    detector = A.build_detector(cfg)

    if args.preview:
        return contact_sheet(cfg)

    if args.roi:
        x, y, w, h = (int(v) for v in args.roi.split(","))
        return store_roi(cfg, x, y, w, h, args.pad)

    if args.pick:
        x, y, w, h = pick_roi(cfg, detector, args)
        return store_roi(cfg, x, y, w, h, args.pad)

    # ---- Batch crop --------------------------------------------------------
    raw_root = C.raw_dir(cfg)
    crops_root = C.crops_dir(cfg)
    photos = data.list_images(raw_root)
    if not photos:
        raise SystemExit(f"no photos under {raw_root} — run scripts/ingest.py first")

    rows, kept, skipped, rejected = [], 0, 0, Counter()
    for path in photos:
        relative = path.relative_to(raw_root).with_suffix(".jpg")
        target = crops_root / relative
        if target.exists() and not args.force:
            skipped += 1
            continue

        image = cv2.imread(str(path))
        if image is None:
            rejected["unreadable"] += 1
            rows.append([str(relative), False, "unreadable file", 0, "", ""])
            continue

        result = pipeline.process(image, cfg, detector)
        metrics = result.metrics
        if result.ok:
            target.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(target), result.crop, [cv2.IMWRITE_JPEG_QUALITY, 95])
            kept += 1
        else:
            rejected[result.reason.split(" (")[0]] += 1
        rows.append([str(relative), result.ok, result.reason, result.n_markers,
                     metrics.get("sharpness", ""), metrics.get("brightness", "")])

    log_path = C.results_dir() / "logs" / f"align_{cfg['component']}.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["photo", "ok", "reason", "markers", "sharpness", "brightness"])
        writer.writerows(rows)

    print(f"cropped {kept}   skipped {skipped} (already done)   rejected {sum(rejected.values())}")
    for reason, n in rejected.most_common():
        print(f"    {n:>4}  {reason}")
    if rejected:
        total = kept + sum(rejected.values())
        if sum(rejected.values()) > 0.2 * max(total, 1):
            print("  more than a fifth rejected — fix the rig before shooting more:")
            print("    fixture not found -> markers must be fully in frame, unglared, flat")
            print("    blurry            -> lock focus with a long press, raise the light")
            print("    too dark / blown  -> move the lamp, lock exposure")
    print(f"  log: {log_path}")
    counts = data.counts(crops_root)
    for label in data.LABELS:
        c = counts[label]
        print(f"  {label:<8} {c['images']:>4} crops across {c['boards']} boards")
    print("next: python scripts/align.py --preview   then   python scripts/split.py")


if __name__ == "__main__":
    main()
