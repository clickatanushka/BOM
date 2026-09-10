#!/usr/bin/env python
"""Generate the printable ArUco marker sheet for the fixture card.

    python scripts/make_markers.py [--mm 40]

Print rig/markers.png at 100% scale (no "fit to page"), cut out the four
squares keeping the white border, and glue them to the corners of a stiff card
in the printed order. The white border is part of the marker: without it the
detector will not see the marker at all.
"""
import argparse

import cv2
import numpy as np

import _boot  # noqa: F401
from polarity import config as C

DPI = 300


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_arg(ap)
    ap.add_argument("--mm", type=float, default=40.0,
                    help="printed size of each marker's black square, in mm (default 40)")
    args = ap.parse_args()
    cfg = C.load(args.config)

    px = int(round(args.mm / 25.4 * DPI))
    quiet = max(px // 5, 20)          # mandatory white border around each marker
    cell = px + 2 * quiet
    label_h = 90

    dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, cfg["aruco_dict"]))
    corners = ["0  TOP-LEFT", "1  TOP-RIGHT", "2  BOTTOM-RIGHT", "3  BOTTOM-LEFT"]
    # Sheet layout matches the physical card: id 0 top-left, 1 top-right,
    # 2 bottom-right, 3 bottom-left.
    positions = {0: (0, 0), 1: (0, 1), 2: (1, 1), 3: (1, 0)}

    sheet = np.full((2 * (cell + label_h) + 160, 2 * cell + 120), 255, np.uint8)
    for slot, marker_id in enumerate(cfg["marker_ids"]):
        row, col = positions[slot]
        img = cv2.aruco.generateImageMarker(dictionary, marker_id, px)
        y = 120 + row * (cell + label_h) + quiet
        x = 60 + col * cell + quiet
        sheet[y:y + px, x:x + px] = img
        cv2.rectangle(sheet, (x - quiet, y - quiet), (x + px + quiet, y + px + quiet), 200, 2)
        cv2.putText(sheet, corners[slot], (x - quiet, y + px + quiet + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, 0, 3)

    cv2.putText(sheet, f"Polarity fixture  |  {cfg['aruco_dict']}  |  "
                       f"print at 100%, each black square = {args.mm:.0f} mm",
                (60, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 0, 2)

    out = C.ROOT / "rig" / "markers.png"
    out.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(out), sheet)
    print(f"wrote {out}")
    print(f"  each marker prints at {args.mm:.0f} mm; keep the grey outline as the white border")
    print("  glue them to the card corners in the printed order, then photograph a board")


if __name__ == "__main__":
    main()
