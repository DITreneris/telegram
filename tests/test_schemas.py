"""parse_manifest elgsenos testai."""

from __future__ import annotations

from pathlib import Path

import pytest

from schemas import MAX_MESSAGE_CHARS, parse_manifest


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


def test_parse_manifest_photo_caption_max_length_ok(tmp_path: Path) -> None:
    img = tmp_path / "shot.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    caption_140 = "x" * 140
    raw = {
        "version": 1,
        "items": [
            {"id": "p", "type": "photo", "path": "shot.png", "caption": caption_140},
        ],
    }
    m = parse_manifest(raw, base_dir=tmp_path)
    assert m.items[0].caption == caption_140


def test_parse_manifest_photo_caption_too_long(tmp_path: Path) -> None:
    img = tmp_path / "shot.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    caption_141 = "x" * 141
    raw = {
        "version": 1,
        "items": [
            {"id": "p", "type": "photo", "path": "shot.png", "caption": caption_141},
        ],
    }
    with pytest.raises(ValueError, match="caption"):
        parse_manifest(raw, base_dir=tmp_path)


def test_parse_manifest_poll_ok(tmp_path: Path) -> None:
    raw = {
        "version": 1,
        "items": [
            {
                "id": "q1",
                "type": "poll",
                "question": "Which is sharper?",
                "options": ["Vague ask", "Role + task + format"],
                "correct_option_id": 1,
                "related_post_id": 3,
                "theme_note": "Guessing vs prompting",
            },
        ],
    }
    m = parse_manifest(raw, base_dir=tmp_path)
    assert len(m.items) == 1
    it = m.items[0]
    assert it.type == "poll"
    assert it.poll_question == "Which is sharper?"
    assert it.poll_options == ("Vague ask", "Role + task + format")
    assert it.poll_correct_option_id == 1
    assert it.related_post_id == 3
    assert it.theme_note == "Guessing vs prompting"


def test_parse_manifest_poll_theme_note_too_long(tmp_path: Path) -> None:
    too_long = "x" * (MAX_MESSAGE_CHARS + 1)
    raw = {
        "version": 1,
        "items": [
            {
                "id": "q1",
                "type": "poll",
                "question": "Q?",
                "options": ["A", "B"],
                "correct_option_id": 0,
                "theme_note": too_long,
            },
        ],
    }
    with pytest.raises(ValueError, match="theme_note"):
        parse_manifest(raw, base_dir=tmp_path)


def test_parse_manifest_poll_correct_id_out_of_range(tmp_path: Path) -> None:
    raw = {
        "version": 1,
        "items": [
            {
                "id": "q1",
                "type": "poll",
                "question": "Q?",
                "options": ["A", "B"],
                "correct_option_id": 2,
            },
        ],
    }
    with pytest.raises(ValueError, match="correct_option_id"):
        parse_manifest(raw, base_dir=tmp_path)


def test_parse_manifest_poll_too_few_options(tmp_path: Path) -> None:
    raw = {
        "version": 1,
        "items": [
            {
                "id": "q1",
                "type": "poll",
                "question": "Q?",
                "options": ["Only one"],
                "correct_option_id": 0,
            },
        ],
    }
    with pytest.raises(ValueError, match="options"):
        parse_manifest(raw, base_dir=tmp_path)


def test_parse_manifest_text_with_related_post_id(tmp_path: Path) -> None:
    raw = {
        "version": 1,
        "items": [
            {"id": "t1", "type": "text", "text": "hi", "related_post_id": 5},
        ],
    }
    m = parse_manifest(raw, base_dir=tmp_path)
    assert m.items[0].related_post_id == 5


def test_parse_manifest_related_post_id_invalid(tmp_path: Path) -> None:
    raw = {
        "version": 1,
        "items": [
            {"id": "t1", "type": "text", "text": "hi", "related_post_id": 0},
        ],
    }
    with pytest.raises(ValueError, match="related_post_id"):
        parse_manifest(raw, base_dir=tmp_path)
