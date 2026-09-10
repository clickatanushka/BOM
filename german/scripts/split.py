#!/usr/bin/env python
"""Split crops into train / validation / test, grouped BY BOARD.

    python scripts/split.py
    python scripts/split.py --dry-run

Why by board: photographing one board fifty times produces fifty nearly
identical images. Splitting those at random puts near-duplicates of a training
image into the test set, and the reported accuracy becomes meaningless. Whole
boards therefore live in exactly one split. The cost is that you need enough
physical boards; five per class is the working minimum.
"""
import argparse
import random
import shutil

import _boot  # noqa: F401
from polarity import config as C
from polarity import data

STAGES = ("train", "val", "test")


def assign_boards(boards, fractions, rng):
    """Give whole boards to stages, guaranteeing val and test are never empty."""
    boards = list(boards)
    rng.shuffle(boards)
    n = len(boards)
    if n < 3:
        raise SystemExit(
            f"only {n} board(s) for this class. A board-level split needs at least 3 "
            "(ideally 5+). Photograph more physical boards before splitting."
        )
    n_test = max(1, round(n * fractions["test"]))
    n_val = max(1, round(n * fractions["val"]))
    if n_test + n_val >= n:                    # keep at least one board for training
        n_test, n_val = 1, 1
    return ({b: "test" for b in boards[:n_test]}
            | {b: "val" for b in boards[n_test:n_test + n_val]}
            | {b: "train" for b in boards[n_test + n_val:]})


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_arg(ap)
    ap.add_argument("--dry-run", action="store_true", help="print the plan, copy nothing")
    args = ap.parse_args()

    cfg = C.load(args.config)
    crops_root = C.crops_dir(cfg)
    split_root = C.split_dir(cfg)
    rng = random.Random(cfg["seed"])

    plan = {}
    for label in data.LABELS:
        boards = data.board_dirs(crops_root, label)
        if not boards:
            raise SystemExit(f"no crops for '{label}' — run scripts/align.py first")
        plan[label] = assign_boards(boards, cfg["split"], rng)

    print(f"seed {cfg['seed']} — the same boards land in the same split on every run\n")
    print(f"{'':10}{'train':>22}{'val':>22}{'test':>22}")
    tally = {}
    for label, assignment in plan.items():
        row = {}
        for stage in STAGES:
            bs = [b for b, s in assignment.items() if s == stage]
            row[stage] = (len(bs), sum(len(data.list_images(b)) for b in bs))
        tally[label] = row
        cells = "".join(f"{f'{v[0]} boards / {v[1]} imgs':>22}" for v in row.values())
        print(f"{label:<10}{cells}")

    print("\nboard assignment:")
    for label, assignment in plan.items():
        for board, stage in sorted(assignment.items(), key=lambda kv: (kv[1], kv[0].name)):
            print(f"  {label:<8} {board.name:<12} -> {stage}")

    test_total = sum(tally[l]["test"][1] for l in data.LABELS)
    if test_total < 60:
        print(f"\n  warning: only {test_total} test images. The gate asks for roughly 200; "
              "the false-PASS figure is weak below that.")

    if args.dry_run:
        print("\ndry run — nothing written")
        return

    if split_root.exists():
        shutil.rmtree(split_root)
    copied = 0
    for label, assignment in plan.items():
        for board, stage in assignment.items():
            target = split_root / stage / label
            target.mkdir(parents=True, exist_ok=True)
            for image in data.list_images(board):
                shutil.copy2(image, target / image.name)
                copied += 1

    (split_root / "SPLIT_MANIFEST.txt").write_text(
        f"component: {cfg['component']}\nseed: {cfg['seed']}\n"
        f"fractions: {cfg['split']}\n\n"
        + "\n".join(f"{label} {board.name} {stage}"
                    for label, a in plan.items() for board, stage in sorted(a.items()))
        + "\n"
    )
    print(f"\nwrote {copied} images to {split_root}")
    print("  board assignment recorded in SPLIT_MANIFEST.txt")
    print("next: python scripts/train.py")


if __name__ == "__main__":
    main()
