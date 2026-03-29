"""Įkelia ir validuoja data/content.json."""

from __future__ import annotations

import json
from pathlib import Path

from schemas import ContentManifest, parse_manifest


def load_content(path: Path, *, base_dir: Path) -> ContentManifest:
    if not path.is_file():
        raise FileNotFoundError(f"Turinio failas nerastas: {path}")
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    return parse_manifest(raw, base_dir=base_dir)
