"""Image quality gates.

A blurred or badly exposed crop must never reach the classifier. In the factory
the honest answer for such a frame is "I cannot see it", not a guess. These
checks run identically during data collection and during the live demo, so the
training data matches what the model sees at inference time.
"""
from __future__ import annotations

import cv2
import numpy as np


def sharpness(image) -> float:
    """Variance of the Laplacian. Higher is sharper. Typical in-focus crop: 100+."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def brightness(image) -> float:
    """Mean grey level, 0-255."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    return float(np.mean(gray))


def check(crop, cfg) -> tuple[bool, str, dict]:
    """Return (ok, reason, metrics) for one crop."""
    s = sharpness(crop)
    b = brightness(crop)
    metrics = {"sharpness": round(s, 1), "brightness": round(b, 1)}
    if s < cfg["blur_threshold"]:
        return False, f"blurry (sharpness {s:.0f} < {cfg['blur_threshold']:.0f})", metrics
    if b < cfg["min_mean_brightness"]:
        return False, f"too dark (brightness {b:.0f})", metrics
    if b > cfg["max_mean_brightness"]:
        return False, f"blown out (brightness {b:.0f})", metrics
    return True, "", metrics
