#!/usr/bin/env python
"""Import photos from the phone into the dataset with standard names and a log.

    python scripts/ingest.py --src ~/Downloads/localsend --label correct --board 01
    python scripts/ingest.py --src ~/Downloads/localsend --label wrong   --board 07 --note "lamp left, 18cm"

Every import is appended to results/logs/ingest.csv so the dataset can be traced
back to a board and a session months later.
"""
import argparse
import csv
import shutil
from datetime import datetime

import _boot  # noqa: F401
from polarity import config as C
from polarity import data


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_config_arg(ap)
    ap.add_argument("--src", required=True, help="folder the phone photos landed in")
    ap.add_argument("--label", required=True, choices=list(data.LABELS))
    ap.add_argument("--board", required=True,
                    help="physical board id, e.g. 01. One id per physical board, "
                         "reused every time you photograph that same board.")
    ap.add_argument("--note", default="", help="lighting / distance / operator note")
    ap.add_argument("--move", action="store_true", help="move files instead of copying")
    args = ap.parse_args()

    cfg = C.load(args.config)
    dest = C.raw_dir(cfg) / args.label / f"board_{args.board}"
    dest.mkdir(parents=True, exist_ok=True)

    sources = data.list_images(args.src)
    if not sources:
        raise SystemExit(f"no images found in {args.src}")

    start = len(data.list_images(dest))
    log_path = C.results_dir() / "logs" / "ingest.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not log_path.exists()

    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["time", "component", "label", "board", "note", "source", "stored"])
        for offset, src in enumerate(sources, start=1):
            name = data.image_name(cfg["component"], args.label, args.board,
                                   start + offset, src.suffix)
            target = dest / name
            (shutil.move if args.move else shutil.copy2)(str(src), str(target))
            writer.writerow([datetime.now().isoformat(timespec="seconds"), cfg["component"],
                             args.label, args.board, args.note, str(src), str(target)])

    print(f"imported {len(sources)} images -> {dest}")
    print(f"  board {args.board} now holds {start + len(sources)} photos")
    counts = data.counts(C.raw_dir(cfg))
    for label in data.LABELS:
        c = counts[label]
        print(f"  {label:<8} {c['images']:>4} images across {c['boards']} boards")
    if counts["wrong"]["boards"] < 3 or counts["correct"]["boards"] < 3:
        print("  note: aim for at least 5 physical boards per class so the "
              "board-level split is meaningful")
    print("next: python scripts/align.py")


if __name__ == "__main__":
    main()
