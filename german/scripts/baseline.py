#!/usr/bin/env python
"""A deliberately simple rule-based checker, for comparison in the report.

    python scripts/baseline.py

A polarity band is a bright stripe at one end of a dark component body, so the
brightness difference between the two halves of the crop carries the signal. The
rule is fitted on the training and validation crops and applied to the test set,
following the same discipline as the model.

This exists to answer the obvious question from the decision meeting: "do we
really need AI for this?" If the rule matches the model, the honest answer is no.
Usually it holds on clean images and collapses on the glare, tilt and
board-to-board colour variation that the model absorbs.
"""
import argparse

import cv2
import numpy as np

import _boot  # noqa: F401
from polarity import config as C
from polarity import data


def features(image):
    """Brightness asymmetry along both axes, normalised by overall brightness."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
    h, w = gray.shape
    mean = max(gray.mean(), 1.0)
    return np.array([
        (gray[:, :w // 2].mean() - gray[:, w // 2:].mean()) / mean,
        (gray[:h // 2].mean() - gray[h // 2:].mean()) / mean,
    ])


def load(root):
    x, y = [], []
    for index, label in enumerate(data.LABELS):
        for path in data.list_images(root / label):
            image = cv2.imread(str(path))
            if image is not None:
                x.append(features(image))
                y.append(index)
    return np.array(x), np.array(y)


def fit(x, y):
    """Pick axis, sign and cut that minimise false PASS first, then false FAIL."""
    best = None
    for axis in (0, 1):
        for sign in (1, -1):
            signal = sign * x[:, axis]
            for cut in np.linspace(signal.min(), signal.max(), 400):
                predicted_wrong = signal >= cut
                false_pass = int(((y == 1) & ~predicted_wrong).sum())
                false_fail = int(((y == 0) & predicted_wrong).sum())
                key = (false_pass, false_fail)
                if best is None or key < best[0]:
                    best = (key, axis, sign, float(cut))
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_arg(ap)
    ap.add_argument("--stage", default="test", choices=["val", "test"],
                    help="which split to report on (default test)")
    args = ap.parse_args()

    cfg = C.load(args.config)
    split_root = C.split_dir(cfg)

    fit_x, fit_y = [], []
    for stage in ("train", "val"):
        x, y = load(split_root / stage)
        if len(x):
            fit_x.append(x)
            fit_y.append(y)
    if not fit_x:
        raise SystemExit("no training crops — run scripts/split.py first")
    fit_x, fit_y = np.vstack(fit_x), np.concatenate(fit_y)

    (fp_fit, ff_fit), axis, sign, cut = fit(fit_x, fit_y)
    axis_name = "left vs right" if axis == 0 else "top vs bottom"
    print(f"rule fitted on train+val: {axis_name} brightness, "
          f"sign {sign:+d}, cut {cut:.4f}")
    print(f"  on the fitting data: false PASS {fp_fit}, false FAIL {ff_fit}")

    x, y = load(split_root / args.stage)
    if not len(x):
        raise SystemExit(f"no {args.stage} crops")
    predicted_wrong = (sign * x[:, axis]) >= cut
    false_pass = int(((y == 1) & ~predicted_wrong).sum())
    false_fail = int(((y == 0) & predicted_wrong).sum())
    n_wrong, n_correct = int((y == 1).sum()), int((y == 0).sum())

    print(f"\nrule-based baseline on the {args.stage} set "
          f"({n_correct} correct, {n_wrong} wrong):")
    print(f"  false PASS {false_pass}  ({false_pass / max(n_wrong, 1) * 100:.1f}% of reversed parts escaped)")
    print(f"  false FAIL {false_fail}  ({false_fail / max(n_correct, 1) * 100:.1f}% of good boards stopped)")

    out = C.results_dir() / "reports" / f"{cfg['component']}_{args.stage}_baseline.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"# Rule-based baseline — {cfg['component']} — {args.stage} set\n\n"
        f"Rule: {axis_name} brightness asymmetry, sign {sign:+d}, cut {cut:.4f}, "
        f"fitted on train+val.\n\n"
        "| Metric | Rule-based |\n|---|---|\n"
        f"| Images | {len(y)} |\n"
        f"| False PASS | {false_pass} |\n"
        f"| False FAIL | {false_fail} |\n\n"
        "Compare against the model numbers in "
        f"`{cfg['component']}_{args.stage}_report.md`. A rule that matches the model "
        "means the AI phase is not justified for this component; a rule that leaks "
        "reversed parts is the argument for it.\n"
    )
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
