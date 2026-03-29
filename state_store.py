"""Vieno naudotojo būsena faile; atomiškas įrašymas."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def default_state() -> dict[str, Any]:
    return {"last_delivered_id": None, "updated_at": None}


def load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return default_state()
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("state.json turi būti objektas.")
    out = default_state()
    lid = data.get("last_delivered_id")
    if lid is not None and not isinstance(lid, str):
        raise ValueError("last_delivered_id turi būti eilutė arba null.")
    out["last_delivered_id"] = lid
    ts = data.get("updated_at")
    if ts is not None and not isinstance(ts, str):
        raise ValueError("updated_at turi būti eilutė arba null.")
    out["updated_at"] = ts
    return out


def save_atomic(path: Path, state: dict[str, Any]) -> None:
    state = dict(state)
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=".state_",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(state, tmp, indent=2, ensure_ascii=False)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
