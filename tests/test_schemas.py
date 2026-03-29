"""parse_manifest elgsenos testai."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from schemas import parse_manifest


def test_parse_manifest_text_ok(tmp_path: Path) -> None:
    raw = {"version": 1, "items": [{"id": "a", "type": "text", "text": "hello"}]}
    m = parse_manifest(raw, base_dir=tmp_path)
    assert m.version == 1
    assert len(m.items) == 1
    assert m.items[0].id == "a"
    assert m.items[0].type == "text"
    assert m.items[0].text == "hello"


def test_parse_manifest_version_invalid(tmp_path: Path) -> None:
    raw = {"version": 2, "items": [{"id": "a", "type": "text", "text": "x"}]}
    with pytest.raises(ValueError, match="version"):
        parse_manifest(raw, base_dir=tmp_path)


def test_parse_manifest_duplicate_id(tmp_path: Path) -> None:
    raw = {
        "version": 1,
        "items": [
            {"id": "a", "type": "text", "text": "1"},
            {"id": "a", "type": "text", "text": "2"},
        ],
    }
    with pytest.raises(ValueError, match="Dubliuotas"):
        parse_manifest(raw, base_dir=tmp_path)


def test_parse_manifest_path_outside_base_dir(tmp_path: Path) -> None:
    sibling = tmp_path.parent / f"sibling_{tmp_path.name}"
    sibling.mkdir(exist_ok=True)
    outside_file = sibling / "secret.txt"
    outside_file.write_text("x", encoding="utf-8")
    rel = Path("..") / sibling.name / "secret.txt"
    raw = {
        "version": 1,
        "items": [{"id": "p", "type": "photo", "path": str(rel).replace("\\", "/")}],
    }
    with pytest.raises(ValueError, match="šaknimi"):
        parse_manifest(raw, base_dir=tmp_path)


def test_parse_manifest_photo_resolves_file(tmp_path: Path) -> None:
    img = tmp_path / "shot.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    raw = {"version": 1, "items": [{"id": "p", "type": "photo", "path": "shot.png"}]}
    m = parse_manifest(raw, base_dir=tmp_path)
    assert m.items[0].type == "photo"
    assert Path(m.items[0].path) == img.resolve()


def test_parse_manifest_document_resolves_file(tmp_path: Path) -> None:
    doc = tmp_path / "note.pdf"
    doc.write_bytes(b"%PDF-1.4")
    raw = {
        "version": 1,
        "items": [{"id": "d", "type": "document", "path": "note.pdf"}],
    }
    m = parse_manifest(raw, base_dir=tmp_path)
    assert m.items[0].type == "document"
    assert Path(m.items[0].path) == doc.resolve()
