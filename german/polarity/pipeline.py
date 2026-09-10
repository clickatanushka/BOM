"""The one path from a phone frame to a model-ready crop.

Training data and the live demo both go through this function, so what the model
learns and what it sees on the line cannot drift apart.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import align, quality


@dataclass
class FrameResult:
    ok: bool                      # True only if aligned AND quality passed
    reason: str                   # why it was rejected, empty when ok
    warped: np.ndarray | None = None      # canonical top-down view
    crop: np.ndarray | None = None        # ROI crop, crop_size square
    markers: list[int] = field(default_factory=list)   # fixture ids found
    metrics: dict = field(default_factory=dict)        # sharpness, brightness

    @property
    def n_markers(self) -> int:
        return len(self.markers)


def process(frame, cfg, detector=None) -> FrameResult:
    """Align a photo to the fixture, cut the ROI, and apply the quality gates."""
    warped, found = align.flatten(frame, cfg, detector)
    if warped is None:
        missing = sorted(set(cfg["marker_ids"]) - set(found))
        return FrameResult(
            ok=False,
            reason=f"fixture not found ({len(found)}/4 markers, missing {missing})",
            markers=found,
        )

    crop = align.crop_roi(warped, cfg)
    ok, reason, metrics = quality.check(crop, cfg)
    return FrameResult(ok=ok, reason=reason, warped=warped, crop=crop,
                       markers=found, metrics=metrics)
