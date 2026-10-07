"""Layered configuration: default.yaml < local.yaml < preset < sidecar yaml < --set overrides."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"


def deep_merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _parse_value(raw: str) -> Any:
    return yaml.safe_load(raw)


def apply_set(cfg: dict, assignments: list[str]) -> dict:
    """Apply `a.b.c=value` overrides (values parsed as YAML)."""
    cfg = copy.deepcopy(cfg)
    for item in assignments or []:
        key, _, raw = item.partition("=")
        node = cfg
        parts = key.strip().split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = _parse_value(raw)
    return cfg


def load_config(preset: str | None = None, sidecar: Path | None = None,
                overrides: list[str] | None = None) -> dict:
    cfg = _load(CONFIG_DIR / "default.yaml")
    cfg = deep_merge(cfg, _load(CONFIG_DIR / "local.yaml"))
    side = _load(sidecar) if sidecar else {}
    preset = side.pop("preset", None) or preset
    if preset:
        presets = _load(CONFIG_DIR / "presets.yaml")
        if preset not in presets:
            raise SystemExit(f"Unknown preset '{preset}'. Available: {', '.join(presets)}")
        cfg = deep_merge(cfg, presets[preset])
        cfg["_preset"] = preset
    cfg = deep_merge(cfg, side)
    cfg = apply_set(cfg, overrides or [])
    cfg["_caption_styles"] = _load(CONFIG_DIR / "caption_styles.yaml")
    cfg["_keywords"] = _load(CONFIG_DIR / "keywords.yaml")
    return cfg


def resolve_path(cfg: dict, key: str) -> Path:
    p = Path(cfg["paths"][key])
    return p if p.is_absolute() else ROOT / p


def resolve_color(cfg: dict, value: str) -> str:
    """Resolve 'brand.primary' style references to hex colours."""
    if isinstance(value, str) and value.startswith("brand."):
        return cfg["brand"][value.split(".", 1)[1]]
    return value
