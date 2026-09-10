#!/usr/bin/env python
"""Fine-tune the correct-vs-wrong classifier.

    python scripts/train.py
    python scripts/train.py --epochs 30 --model mobilenetv3_small_100

Class 0 is 'correct', class 1 is 'wrong'; the model outputs P(wrong).

Augmentation deliberately excludes horizontal flips, vertical flips and 180
degree rotation. Those operations turn a correctly placed part into a reversed
one without changing the label, which would teach the model that a reversed part
is acceptable. Only photometric changes and small geometric jitter are used.
"""
import argparse
import hashlib
import json
import random
import time
from datetime import datetime

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision import transforms as T

import _boot  # noqa: F401
from polarity import config as C
from polarity import model as M


def make_transforms(cfg):
    size = cfg["img_size"] if "img_size" in cfg else cfg["crop_size"]
    a = cfg["aug"]
    normalize = T.Normalize(M.IMAGENET_MEAN.tolist(), M.IMAGENET_STD.tolist())
    train = T.Compose([
        T.Resize((size, size)),
        T.ColorJitter(brightness=a["brightness"], contrast=a["contrast"],
                      saturation=a["saturation"], hue=a["hue"]),
        T.RandomApply([T.GaussianBlur(3, sigma=(0.1, 1.2))], p=a["blur_p"]),
        T.RandomAffine(degrees=a["rotate_deg"],
                       translate=(a["translate"], a["translate"]),
                       scale=(1 - a["scale_jitter"], 1 + a["scale_jitter"])),
        T.ToTensor(), normalize,
    ])
    evaluate = T.Compose([T.Resize((size, size)), T.ToTensor(), normalize])
    return train, evaluate, size


def evaluate_epoch(model, loader, criterion, device):
    """Val loss, accuracy, and the safety headroom we actually care about."""
    model.eval()
    total_loss, correct, probs, labels = 0.0, 0, [], []
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            total_loss += criterion(logits, y).item() * len(x)
            correct += (logits.argmax(1) == y).sum().item()
            probs.append(torch.softmax(logits, 1)[:, 1].cpu().numpy())
            labels.append(y.cpu().numpy())
    probs = np.concatenate(probs) if probs else np.empty(0)
    labels = np.concatenate(labels) if labels else np.empty(0)
    n = max(len(labels), 1)
    # The lowest P(wrong) the model gives any genuinely wrong image. The FAIL
    # threshold has to sit below this, so the higher it is the more headroom
    # there is before a reversed part slips through.
    weakest_wrong = float(probs[labels == 1].min()) if (labels == 1).any() else float("nan")
    strongest_correct = float(probs[labels == 0].max()) if (labels == 0).any() else float("nan")
    return total_loss / n, correct / n, weakest_wrong, strongest_correct


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_arg(ap)
    ap.add_argument("--epochs", type=int)
    ap.add_argument("--model")
    ap.add_argument("--batch-size", type=int)
    ap.add_argument("--lr", type=float)
    ap.add_argument("--workers", type=int)
    args = ap.parse_args()

    cfg = C.load(args.config)
    for key, value in (("epochs", args.epochs), ("model", args.model),
                       ("batch_size", args.batch_size), ("lr", args.lr),
                       ("num_workers", args.workers)):
        if value is not None:
            cfg[key] = value

    torch.manual_seed(cfg["seed"])
    random.seed(cfg["seed"])
    np.random.seed(cfg["seed"])

    split_root = C.split_dir(cfg)
    if not (split_root / "train").exists():
        raise SystemExit(f"no split at {split_root} — run scripts/split.py first")

    train_tf, eval_tf, size = make_transforms(cfg)
    train_set = datasets.ImageFolder(split_root / "train", train_tf)
    val_set = datasets.ImageFolder(split_root / "val", eval_tf)

    if tuple(train_set.classes) != M.CLASSES:
        raise SystemExit(
            f"class folders are {train_set.classes}, expected {list(M.CLASSES)}.\n"
            "The order decides which output means 'wrong'. Fix the folder names."
        )

    device = M.device()
    counts = np.bincount([y for _, y in train_set.samples], minlength=2)
    print(f"train {len(train_set)} images (correct {counts[0]}, wrong {counts[1]})   "
          f"val {len(val_set)}   device {device}")
    if min(counts) == 0:
        raise SystemExit("one class has no training images")

    workers = cfg["num_workers"] if device == "cuda" else min(cfg["num_workers"], 4)
    train_loader = DataLoader(train_set, cfg["batch_size"], shuffle=True,
                              num_workers=workers, drop_last=len(train_set) > cfg["batch_size"])
    val_loader = DataLoader(val_set, cfg["batch_size"], shuffle=False, num_workers=workers)

    model, used_pretrained = M.build(cfg)
    model.to(device)

    # Imbalance correction, then an extra nudge: missing a reversed part costs
    # more than over-rejecting a good one, so 'wrong' carries more loss weight.
    balance = counts[0] / max(counts[1], 1)
    weights = torch.tensor([1.0, balance * cfg["wrong_class_weight"]], dtype=torch.float32)
    print(f"class weights: correct 1.00, wrong {weights[1]:.2f}"
          f" (imbalance {balance:.2f} x safety {cfg['wrong_class_weight']})")
    criterion = nn.CrossEntropyLoss(weight=weights.to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg["lr"],
                                  weight_decay=cfg["weight_decay"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg["epochs"])

    model_path = C.model_path(cfg)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    history, best_loss, stale = [], float("inf"), 0

    print(f"\n{'ep':>3} {'train':>8} {'val':>8} {'acc':>6} {'min P(wrong)':>13} "
          f"{'max P(correct)':>15} {'sec':>5}")
    print("-" * 64)
    for epoch in range(1, cfg["epochs"] + 1):
        started = time.time()
        model.train()
        running = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            running += loss.item() * len(x)
        scheduler.step()
        train_loss = running / max(len(train_set), 1)
        val_loss, val_acc, weakest_wrong, strongest_correct = evaluate_epoch(
            model, val_loader, criterion, device)
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss,
                        "val_acc": val_acc, "min_p_wrong_on_wrong": weakest_wrong,
                        "max_p_wrong_on_correct": strongest_correct})
        marker = ""
        if val_loss < best_loss:
            best_loss, stale, marker = val_loss, 0, "  <- best"
            torch.save({"model": cfg["model"], "state": model.state_dict(),
                        "classes": list(M.CLASSES), "img_size": size,
                        "component": cfg["component"], "seed": cfg["seed"],
                        "pretrained": used_pretrained,
                        "trained_at": datetime.now().isoformat(timespec="seconds")},
                       model_path)
        else:
            stale += 1
        print(f"{epoch:>3} {train_loss:>8.4f} {val_loss:>8.4f} {val_acc:>6.3f} "
              f"{weakest_wrong:>13.3f} {strongest_correct:>15.3f} "
              f"{time.time() - started:>5.0f}{marker}")
        if stale >= cfg["patience"]:
            print(f"early stop: no improvement for {cfg['patience']} epochs")
            break

    sha = hashlib.sha256(model_path.read_bytes()).hexdigest()
    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
    checkpoint["sha"] = sha[:16]
    torch.save(checkpoint, model_path)

    meta = {"component": cfg["component"], "architecture": cfg["model"],
            "pretrained": used_pretrained, "seed": cfg["seed"],
            "img_size": size, "epochs_run": len(history),
            "best_val_loss": best_loss, "train_images": len(train_set),
            "val_images": len(val_set), "model_sha256_16": sha[:16],
            "trained_at": datetime.now().isoformat(timespec="seconds"),
            "history": history}
    meta_path = model_path.with_name(f"{cfg['component']}_train_meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))

    print(f"\nsaved {model_path}  (sha {sha[:16]})")
    print(f"      {meta_path}")
    last = history[-1]
    if not np.isnan(last["min_p_wrong_on_wrong"]):
        gap = last["min_p_wrong_on_wrong"] - last["max_p_wrong_on_correct"]
        print(f"  separation on val: weakest wrong {last['min_p_wrong_on_wrong']:.3f} vs "
              f"strongest correct {last['max_p_wrong_on_correct']:.3f}  (gap {gap:+.3f})")
        if gap <= 0:
            print("  the classes overlap: no threshold gives zero false PASS without "
                  "many false FAILs. Add more varied wrong boards.")
    print("next: python scripts/evaluate.py --stage val")


if __name__ == "__main__":
    main()
