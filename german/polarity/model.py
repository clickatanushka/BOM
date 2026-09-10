"""Classifier construction, checkpoint loading, and the PASS/CHECK/FAIL rule."""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import torch

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# Index 0 = correct, index 1 = wrong. torchvision.datasets.ImageFolder sorts
# class folders alphabetically, which gives exactly this order. Asserted at
# training time so a renamed folder can never silently invert the meaning.
CLASSES = ("correct", "wrong")

PASS, CHECK, FAIL = "PASS", "CHECK", "FAIL"


def device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def build(cfg, pretrained: bool | None = None):
    """Create the backbone with a two-class head, falling back to random init offline."""
    import timm

    want = cfg["pretrained"] if pretrained is None else pretrained
    if want:
        try:
            return timm.create_model(cfg["model"], pretrained=True, num_classes=2), True
        except Exception as exc:  # no network, or the weight cache is empty
            print(f"  ! pretrained weights unavailable ({type(exc).__name__}); "
                  f"training from scratch, expect to need more data")
    return timm.create_model(cfg["model"], pretrained=False, num_classes=2), False


def preprocess(crops, size: int) -> torch.Tensor:
    """BGR uint8 crops -> normalised NCHW float tensor. Mirrors the eval transform."""
    batch = []
    for c in crops:
        if c.shape[0] != size or c.shape[1] != size:
            c = cv2.resize(c, (size, size), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(c, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        batch.append(((rgb - IMAGENET_MEAN) / IMAGENET_STD).transpose(2, 0, 1))
    return torch.from_numpy(np.ascontiguousarray(np.stack(batch)))


class Classifier:
    """Loads a checkpoint and returns P(wrong) for crops."""

    def __init__(self, checkpoint: Path):
        import timm

        if not Path(checkpoint).exists():
            raise SystemExit(
                f"no trained model at {checkpoint}\nRun:  python scripts/train.py"
            )
        ckpt = torch.load(checkpoint, map_location="cpu", weights_only=False)
        self.classes = tuple(ckpt.get("classes", CLASSES))
        if self.classes != CLASSES:
            raise SystemExit(f"checkpoint class order is {self.classes}, expected {CLASSES}")
        self.size = ckpt["img_size"]
        self.arch = ckpt["model"]
        self.sha = ckpt.get("sha", "")
        self.model = timm.create_model(self.arch, pretrained=False, num_classes=2)
        self.model.load_state_dict(ckpt["state"])
        self.device = device()
        self.model.to(self.device).eval()

    @torch.no_grad()
    def p_wrong(self, crops) -> np.ndarray:
        """Probability that each crop shows a reversed part."""
        if not len(crops):
            return np.empty(0, dtype=np.float32)
        x = preprocess(crops, self.size).to(self.device)
        probs = torch.softmax(self.model(x), dim=1)[:, 1]
        return probs.cpu().numpy().astype(np.float32)


def decide(p_wrong: float, fail_threshold: float, check_threshold: float) -> str:
    """Three-state decision. Deliberately biased towards stopping the board.

    The deck proposed a single lenient cut ("FAIL if wrong >= 80%"). That leaves
    reversed parts passing. We instead fail easily and route the uncertain band
    to a human, because an over-rejected good board costs a recheck while an
    escaped bad board reaches the customer.
    """
    if p_wrong >= fail_threshold:
        return FAIL
    if p_wrong >= check_threshold:
        return CHECK
    return PASS


def load_thresholds(cfg, path: Path) -> tuple[float, float, str]:
    """Prefer thresholds chosen on the validation set; fall back to config."""
    if Path(path).exists():
        t = json.loads(Path(path).read_text())
        return t["fail_threshold"], t["check_threshold"], "validation set"
    return cfg["fail_threshold"], cfg["check_threshold"], "config.yaml cold start"
