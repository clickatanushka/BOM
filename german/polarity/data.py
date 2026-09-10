"""Dataset walking, naming and board-level grouping.

The board id is the unit that must never straddle a train/test boundary, so it
is baked into the folder layout: dataset/<stage>/<component>/<label>/board_XX/.
"""
from __future__ import annotations

import re
from pathlib import Path

LABELS = ("correct", "wrong")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".heic", ".HEIC"}
BOARD_RE = re.compile(r"board_([A-Za-z0-9]+)")
# Split folders hold files flat, so the board id has to be recoverable from the
# file name too: D12_wrong_bS04_0007.jpg -> S04
NAME_BOARD_RE = re.compile(r"_b([A-Za-z0-9]+)_\d+$")


def list_images(directory) -> list[Path]:
    d = Path(directory)
    if not d.exists():
        return []
    return sorted(p for p in d.rglob("*") if p.suffix.lower() in {s.lower() for s in IMAGE_SUFFIXES})


def board_dirs(root: Path, label: str) -> list[Path]:
    d = root / label
    if not d.exists():
        return []
    return sorted(p for p in d.glob("board_*") if p.is_dir())


def board_id_of(path: Path) -> str:
    """Pull the board id out of any path under the dataset tree.

    Works both for the raw/crops layout (.../board_S04/photo.jpg) and for the
    split layout, where files sit flat and the id survives only in the name.
    """
    for part in path.parts:
        m = BOARD_RE.fullmatch(part)
        if m:
            return m.group(1)
    m = NAME_BOARD_RE.search(Path(path).stem)
    return m.group(1) if m else "unknown"


def counts(root: Path) -> dict[str, dict[str, int]]:
    """{label: {'boards': n, 'images': n}} for a raw or crops tree."""
    out = {}
    for label in LABELS:
        boards = board_dirs(root, label)
        out[label] = {
            "boards": len(boards),
            "images": sum(len(list_images(b)) for b in boards),
        }
    return out


def image_name(component: str, label: str, board: str, index: int, suffix: str = ".jpg") -> str:
    """D12_correct_b03_0007.jpg — component, label, board, running index."""
    return f"{component}_{label}_b{board}_{index:04d}{suffix.lower()}"
