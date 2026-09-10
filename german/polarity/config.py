"""Configuration loading. One YAML file per component."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config.yaml"


def load(path: str | Path | None = None) -> dict[str, Any]:
    """Read a config file and attach its own path under '_path' so save() round-trips."""
    p = Path(path) if path else DEFAULT_CONFIG
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        raise SystemExit(f"config not found: {p}")
    with open(p) as f:
        cfg = yaml.safe_load(f)
    cfg["_path"] = str(p)
    return cfg


def save(cfg: dict[str, Any]) -> None:
    """Write the config back, preserving key order and dropping internal keys."""
    p = Path(cfg.get("_path", DEFAULT_CONFIG))
    out = {k: v for k, v in cfg.items() if not k.startswith("_")}
    with open(p, "w") as f:
        yaml.safe_dump(out, f, sort_keys=False, default_flow_style=False)


def add_config_arg(parser) -> None:
    """Every script takes --config so a second component is one flag away."""
    parser.add_argument(
        "--config",
        default=None,
        help="path to a config YAML (default: config.yaml at the project root)",
    )


# ---- Derived paths ---------------------------------------------------------
def raw_dir(cfg) -> Path:
    return ROOT / "dataset" / "raw" / cfg["component"]


def crops_dir(cfg) -> Path:
    return ROOT / "dataset" / "crops" / cfg["component"]


def split_dir(cfg) -> Path:
    return ROOT / "dataset" / "split" / cfg["component"]


def model_path(cfg) -> Path:
    return ROOT / "models" / f"{cfg['component']}_best.pt"


def threshold_path(cfg) -> Path:
    return ROOT / "models" / f"{cfg['component']}_threshold.json"


def results_dir() -> Path:
    return ROOT / "results"
