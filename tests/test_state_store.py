"""state_store load/save_atomic elgsena."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from state_store import default_state, load, save_atomic


def test_load_missing_file_returns_default(tmp_path: Path) -> None:
    missing = tmp_path / "state.json"
    assert not missing.is_file()
    st = load(missing)
    assert st == default_state()


def test_load_invalid_json_raises(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load(path)


def test_load_root_not_object_raises(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text("[1,2,3]", encoding="utf-8")
    with pytest.raises(ValueError, match="objektas"):
        load(path)


def test_save_atomic_writes_valid_json_and_timestamp(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    save_atomic(path, {"last_delivered_id": "item_a", "updated_at": None})
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["last_delivered_id"] == "item_a"
    assert data.get("updated_at") is not None
    st = load(path)
    assert st["last_delivered_id"] == "item_a"
    assert st.get("updated_at") is not None
