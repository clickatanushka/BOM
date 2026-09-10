"""Fixture alignment.

The board sits on a card with four ArUco markers at its corners. Finding those
four markers gives an exact mapping from any phone photo to one canonical
top-down view, so the component always lands on the same pixels and the ROI can
be a fixed rectangle. This is far more robust than detecting board edges, and it
absorbs small changes in phone height, tilt and rotation between sessions.
"""
from __future__ import annotations

import cv2
import numpy as np


def build_detector(cfg):
    dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, cfg["aruco_dict"]))
    params = cv2.aruco.DetectorParameters()
    # The markers are printed small and may be slightly out of focus at the edge
    # of the frame; widen the adaptive threshold sweep to find them anyway.
    params.adaptiveThreshWinSizeMin = 3
    params.adaptiveThreshWinSizeMax = 33
    params.adaptiveThreshWinSizeStep = 4
    # Sub-pixel corner refinement: the homography is only as good as the corners.
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    return cv2.aruco.ArucoDetector(dictionary, params)


def canonical_marker_points(cfg) -> np.ndarray:
    """Where the four marker centres must land in the flattened view.

    Order follows cfg['marker_ids']: top-left, top-right, bottom-right, bottom-left.
    """
    w, h = cfg["canonical_width"], cfg["canonical_height"]
    m = cfg["marker_inset"]
    return np.float32([[m, m], [w - m, m], [w - m, h - m], [m, h - m]])


def find_markers(image, cfg, detector=None) -> dict[int, np.ndarray]:
    """Return {marker_id: centre_xy} for the fixture markers present in the image."""
    detector = detector or build_detector(cfg)
    corners, ids, _ = detector.detectMarkers(image)
    if ids is None:
        return {}
    wanted = set(cfg["marker_ids"])
    return {
        int(i): c[0].mean(axis=0)
        for c, i in zip(corners, ids.flatten())
        if int(i) in wanted
    }


def flatten(image, cfg, detector=None):
    """Warp a phone photo to the canonical top-down view.

    Returns (warped, found_ids). warped is None when fewer than cfg['min_markers']
    fixture markers were located, which usually means the card is partly out of
    frame, the lighting has collapsed, or a marker is covered.
    """
    centres = find_markers(image, cfg, detector)
    found = sorted(centres)
    if len(centres) < cfg["min_markers"]:
        return None, found

    order = [i for i in cfg["marker_ids"] if i in centres]
    src = np.float32([centres[i] for i in order])
    dst_all = canonical_marker_points(cfg)
    dst = np.float32([dst_all[cfg["marker_ids"].index(i)] for i in order])

    if len(order) == 4:
        matrix = cv2.getPerspectiveTransform(src, dst)
    else:
        matrix, _ = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    if matrix is None:
        return None, found

    warped = cv2.warpPerspective(
        image, matrix, (cfg["canonical_width"], cfg["canonical_height"]),
        flags=cv2.INTER_LINEAR,
    )
    return warped, found


def crop_roi(warped, cfg):
    """Cut the component ROI out of a flattened image and resize to the model input."""
    r = cfg["roi"]
    if r["w"] <= 0 or r["h"] <= 0:
        raise SystemExit(
            "ROI is not set yet.\n"
            "Run:  python scripts/align.py --pick\n"
            "then drag a box around the component and press ENTER."
        )
    x, y = max(0, r["x"]), max(0, r["y"])
    crop = warped[y:y + r["h"], x:x + r["w"]]
    if crop.size == 0:
        raise SystemExit(f"ROI {r} falls outside the canonical image. Re-run --pick.")
    size = cfg["crop_size"]
    return cv2.resize(crop, (size, size), interpolation=cv2.INTER_AREA)
