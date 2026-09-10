#!/usr/bin/env python
"""Check that this laptop can run the pipeline, and report the project state.

    python scripts/doctor.py

Run it first, and again whenever something behaves oddly.
"""
import argparse

import _boot  # noqa: F401
from polarity import config as C
from polarity import data


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    C.add_config_arg(ap)
    args = ap.parse_args()

    print("=" * 68)
    print("  POLARITY GATE — environment and project check")
    print("=" * 68)

    ok = True

    # ---- Libraries ---------------------------------------------------------
    try:
        import cv2
        print(f"  opencv            {cv2.__version__}")
        if not hasattr(cv2, "aruco"):
            print("  ! cv2.aruco missing. Install opencv-contrib-python, not opencv-python.")
            ok = False
    except ImportError:
        print("  ! opencv not installed"); ok = False

    try:
        import torch
        print(f"  torch             {torch.__version__}")
        if torch.cuda.is_available():
            print(f"  device            cuda ({torch.cuda.get_device_name(0)})")
        else:
            print(f"  device            cpu ({torch.get_num_threads()} threads) — fine for this model size")
    except ImportError:
        print("  ! torch not installed"); ok = False

    try:
        import timm
        print(f"  timm              {timm.__version__}")
    except ImportError:
        print("  ! timm not installed"); ok = False

    # ---- Display (needed for --pick and the live HMI) ----------------------
    try:
        import cv2
        cv2.namedWindow("_probe")
        cv2.destroyWindow("_probe")
        print("  display           available (ROI picker and HMI will open)")
    except Exception:
        print("  display           NOT available — use --roi on align.py and "
              "--save-frames on hmi.py instead of the live window")

    # ---- Config ------------------------------------------------------------
    cfg = C.load(args.config)
    print("-" * 68)
    print(f"  config            {cfg['_path']}")
    print(f"  component         {cfg['component']} ({cfg['component_kind']})")
    roi = cfg["roi"]
    if roi["w"] > 0:
        print(f"  ROI               x={roi['x']} y={roi['y']} {roi['w']}x{roi['h']} px")
    else:
        print("  ROI               NOT SET — run: python scripts/align.py --pick")

    # ---- Data --------------------------------------------------------------
    print("-" * 68)
    for name, root in (("raw photos", C.raw_dir(cfg)), ("crops", C.crops_dir(cfg))):
        c = data.counts(root)
        print(f"  {name:<17} "
              f"correct: {c['correct']['images']:>4} imgs / {c['correct']['boards']} boards   "
              f"wrong: {c['wrong']['images']:>4} imgs / {c['wrong']['boards']} boards")

    split_root = C.split_dir(cfg)
    if split_root.exists():
        parts = []
        for stage in ("train", "val", "test"):
            n = sum(len(data.list_images(split_root / stage / lab)) for lab in data.LABELS)
            parts.append(f"{stage} {n}")
        print(f"  split             {'   '.join(parts)}")
    else:
        print("  split             not built yet — run: python scripts/split.py")

    mp, tp = C.model_path(cfg), C.threshold_path(cfg)
    print(f"  model             {'trained: ' + mp.name if mp.exists() else 'not trained yet'}")
    if tp.exists():
        import json
        t = json.loads(tp.read_text())
        print(f"  thresholds        FAIL >= {t['fail_threshold']}   CHECK >= {t['check_threshold']}")
    else:
        print("  thresholds        not chosen yet — run: python scripts/evaluate.py --stage val")

    print("=" * 68)
    print("  next step:", next_step(cfg, mp, tp, split_root))
    print("=" * 68)
    return 0 if ok else 1


def next_step(cfg, model_path, thr_path, split_root):
    if data.counts(C.raw_dir(cfg))["correct"]["images"] == 0:
        return "build the rig, then shoot correct boards and run scripts/ingest.py"
    if cfg["roi"]["w"] <= 0:
        return "python scripts/align.py --pick"
    if data.counts(C.crops_dir(cfg))["correct"]["images"] == 0:
        return "python scripts/align.py"
    if data.counts(C.raw_dir(cfg))["wrong"]["images"] == 0:
        return "get reversed boards from the factory, shoot them, ingest with --label wrong"
    if not split_root.exists():
        return "python scripts/split.py"
    if not model_path.exists():
        return "python scripts/train.py"
    if not thr_path.exists():
        return "python scripts/evaluate.py --stage val"
    return "python scripts/evaluate.py --stage test   (once only), then scripts/hmi.py"


if __name__ == "__main__":
    raise SystemExit(main())
