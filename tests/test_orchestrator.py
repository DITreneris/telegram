"""Orchestrator eilės ir būsenos testai su tmp_path."""

from __future__ import annotations

import json
from pathlib import Path

from orchestrator import Orchestrator
from state_store import load as load_state


def test_orchestrator_cycle_and_state(tmp_path: Path) -> None:
    content = {
        "version": 1,
        "items": [
            {"id": "first", "type": "text", "text": "one"},
            {"id": "second", "type": "text", "text": "two"},
        ],
    }
    content_path = tmp_path / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
    state_path = tmp_path / "state.json"

    orch = Orchestrator(
        content_path=content_path,
        state_path=state_path,
        base_dir=tmp_path,
    )

    a = orch.peek_next_item()
    assert a.id == "first"
    assert a.text == "one"
    orch.record_delivered(a.id)
    st = load_state(state_path)
    assert st["last_delivered_id"] == "first"
    assert st.get("updated_at") is not None

    b = orch.peek_next_item()
    assert b.id == "second"
    orch.record_delivered(b.id)
    st = load_state(state_path)
    assert st["last_delivered_id"] == "second"

    c = orch.peek_next_item()
    assert c.id == "first"
    orch.record_delivered(c.id)
    st = load_state(state_path)
    assert st["last_delivered_id"] == "first"


def test_orchestrator_unknown_last_id_restarts_from_first(tmp_path: Path) -> None:
    content = {
        "version": 1,
        "items": [
            {"id": "a", "type": "text", "text": "A"},
            {"id": "b", "type": "text", "text": "B"},
        ],
    }
    content_path = tmp_path / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
    state_path = tmp_path / "state.json"
    state_path.write_text(
        json.dumps({"last_delivered_id": "missing", "updated_at": None}),
        encoding="utf-8",
    )

    orch = Orchestrator(
        content_path=content_path,
        state_path=state_path,
        base_dir=tmp_path,
    )
    nxt = orch.peek_next_item()
    assert nxt.id == "a"
    orch.record_delivered(nxt.id)
    st = load_state(state_path)
    assert st["last_delivered_id"] == "a"


def test_peek_without_record_keeps_state(tmp_path: Path) -> None:
    content = {
        "version": 1,
        "items": [
            {"id": "first", "type": "text", "text": "one"},
            {"id": "second", "type": "text", "text": "two"},
        ],
    }
    content_path = tmp_path / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
    state_path = tmp_path / "state.json"
    state_path.write_text(
        json.dumps({"last_delivered_id": "first", "updated_at": "2020-01-01T00:00:00+00:00"}),
        encoding="utf-8",
    )

    orch = Orchestrator(
        content_path=content_path,
        state_path=state_path,
        base_dir=tmp_path,
    )
    item = orch.peek_next_item()
    assert item.id == "second"
    st = load_state(state_path)
    assert st["last_delivered_id"] == "first"
    assert st.get("updated_at") == "2020-01-01T00:00:00+00:00"


def test_status_text_next_matches_peek_initial_state(tmp_path: Path) -> None:
    content = {
        "version": 1,
        "items": [
            {"id": "first", "type": "text", "text": "one"},
            {"id": "second", "type": "text", "text": "two"},
        ],
    }
    content_path = tmp_path / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
    state_path = tmp_path / "state.json"

    orch = Orchestrator(
        content_path=content_path,
        state_path=state_path,
        base_dir=tmp_path,
    )
    peek = orch.peek_next_item()
    text = orch.status_text()
    assert peek.id == "first" and peek.type == "text"
    assert "Items: 2" in text
    assert "Last delivered id: None" in text
    assert "Next: id=first, type=text" in text


def test_status_text_next_matches_peek_after_delivery(tmp_path: Path) -> None:
    content = {
        "version": 1,
        "items": [
            {"id": "first", "type": "text", "text": "one"},
            {"id": "second", "type": "text", "text": "two"},
        ],
    }
    content_path = tmp_path / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
    state_path = tmp_path / "state.json"

    orch = Orchestrator(
        content_path=content_path,
        state_path=state_path,
        base_dir=tmp_path,
    )
    orch.record_delivered("first")
    peek = orch.peek_next_item()
    text = orch.status_text()
    assert peek.id == "second" and peek.type == "text"
    assert "Last delivered id: 'first'" in text
    assert "Next: id=second, type=text" in text


def test_status_text_next_when_last_unknown_matches_peek(tmp_path: Path) -> None:
    content = {
        "version": 1,
        "items": [
            {"id": "a", "type": "text", "text": "A"},
            {"id": "b", "type": "text", "text": "B"},
        ],
    }
    content_path = tmp_path / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
    state_path = tmp_path / "state.json"
    state_path.write_text(
        json.dumps({"last_delivered_id": "missing", "updated_at": None}),
        encoding="utf-8",
    )

    orch = Orchestrator(
        content_path=content_path,
        state_path=state_path,
        base_dir=tmp_path,
    )
    peek = orch.peek_next_item()
    text = orch.status_text()
    assert peek.id == "a"
    assert "Next: id=a, type=text" in text


def test_orchestrator_mark_x_posted_and_is_x_posted(tmp_path: Path) -> None:
    content = {"version": 1, "items": [{"id": "a", "type": "text", "text": "A"}]}
    content_path = tmp_path / "content.json"
    content_path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
    state_path = tmp_path / "state.json"
    orch = Orchestrator(
        content_path=content_path,
        state_path=state_path,
        base_dir=tmp_path,
    )
    assert orch.is_x_posted("x1") is False
    orch.mark_x_posted("x1")
    assert orch.is_x_posted("x1") is True
    orch.mark_x_posted("x1")
    st = load_state(state_path)
    assert st["x_posted_item_ids"] == ["x1"]
