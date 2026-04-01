"""queue_manifest_sync: build manifest from posts + polls bank."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from queue_manifest_sync import (
    build_and_validate_manifest,
    build_manifest_dict,
    effective_topic_key,
    hook_caption,
    image_to_relative_path,
    journey_order_path,
    load_poll_bank,
    load_posts_rows,
    order_posts_for_journey,
    resolve_post_order,
    validate_journey_order_ids,
    validate_poll_post_ids,
)
from schemas import MAX_CAPTION_CHARS


def test_hook_caption_truncates() -> None:
    long = "x" * 200
    cap = hook_caption(long)
    assert len(cap) == MAX_CAPTION_CHARS
    assert cap.endswith("...")


def test_image_to_relative_path() -> None:
    assert image_to_relative_path("/images/posts/01.png") == "web/public/images/posts/01.png"


def test_validate_poll_post_ids_raises() -> None:
    with pytest.raises(ValueError, match="not found"):
        validate_poll_post_ids(
            [{"id": "q1", "related_post_id": 99}],
            {1},
        )


def test_build_manifest_minimal_chain(tmp_path: Path) -> None:
    img_dir = tmp_path / "web" / "public" / "images" / "posts"
    img_dir.mkdir(parents=True)
    (img_dir / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    posts_path = tmp_path / "web" / "public" / "posts.json"
    posts_path.write_text(
        json.dumps(
            [
                {
                    "id": 2,
                    "theme": "B theme",
                    "content": "Body B",
                    "image": "/images/posts/missing.png",
                },
                {
                    "id": 1,
                    "theme": "A theme",
                    "content": "Body A",
                    "image": "/images/posts/a.png",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    polls_path = tmp_path / "data" / "polls.json"
    polls_path.parent.mkdir(parents=True, exist_ok=True)
    polls_path.write_text(
        json.dumps(
            {
                "version": 1,
                "items": [
                    {
                        "id": "quiz_1",
                        "related_post_id": 1,
                        "question": "Q1?",
                        "options": ["Wrong", "Right"],
                        "correct_option_id": 1,
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    posts = load_posts_rows(posts_path)
    polls = load_poll_bank(polls_path)
    raw = build_manifest_dict(base_dir=tmp_path, posts=posts, polls=polls)
    ids = [it["id"] for it in raw["items"]]
    assert ids == [
        "post_001_photo",
        "post_001_text",
        "quiz_1",
        "post_002_text",
    ]


def test_effective_topic_key_prefers_explicit() -> None:
    row = {"id": 1, "theme": "Hello", "content": "x", "topic_key": "explicit_slug"}
    assert effective_topic_key(row) == "explicit_slug"


def test_load_posts_rejects_blank_topic_key(tmp_path: Path) -> None:
    posts_path = tmp_path / "posts.json"
    posts_path.write_text(
        json.dumps(
            [{"id": 1, "theme": "T", "content": "c", "topic_key": "  "}],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="topic_key"):
        load_posts_rows(posts_path)


def test_order_posts_for_journey_no_adjacent_same_topic_when_spacer_exists() -> None:
    posts = [
        {"id": 1, "theme": "Same headline", "content": "a", "topic_key": "t"},
        {"id": 2, "theme": "Same headline", "content": "b", "topic_key": "t"},
        {"id": 3, "theme": "Other", "content": "c", "topic_key": "u"},
    ]
    out = order_posts_for_journey(posts)
    assert [int(p["id"]) for p in out] == [1, 3, 2]
    keys = [effective_topic_key(p) for p in out]
    assert keys[0] != keys[1]
    assert keys[1] != keys[2]


def test_resolve_post_order_uses_journey_file(tmp_path: Path) -> None:
    img_dir = tmp_path / "web" / "public" / "images" / "posts"
    img_dir.mkdir(parents=True)
    (img_dir / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    posts_path = tmp_path / "web" / "public" / "posts.json"
    posts_path.write_text(
        json.dumps(
            [
                {"id": 2, "theme": "B", "content": "b", "image": "/images/posts/missing.png"},
                {"id": 1, "theme": "A", "content": "a", "image": "/images/posts/a.png"},
                {"id": 3, "theme": "C", "content": "c"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    polls_path = tmp_path / "data" / "polls.json"
    polls_path.parent.mkdir(parents=True, exist_ok=True)
    polls_path.write_text(
        json.dumps({"version": 1, "items": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    jpath = journey_order_path(tmp_path)
    jpath.parent.mkdir(parents=True, exist_ok=True)
    jpath.write_text(
        json.dumps({"version": 1, "post_ids": [3, 1, 2]}, ensure_ascii=False),
        encoding="utf-8",
    )
    posts = load_posts_rows(posts_path)
    polls = load_poll_bank(polls_path)
    raw = build_manifest_dict(base_dir=tmp_path, posts=posts, polls=polls)
    text_ids = [
        it["related_post_id"] for it in raw["items"] if it["type"] == "text"
    ]
    assert text_ids == [3, 1, 2]


def test_validate_journey_order_ids_rejects_duplicate() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        validate_journey_order_ids(post_ids=[1, 1, 2], valid_ids={1, 2, 3})


def test_validate_journey_order_ids_rejects_wrong_size() -> None:
    with pytest.raises(ValueError, match="expected 2"):
        validate_journey_order_ids(post_ids=[1], valid_ids={1, 2})


def test_build_and_validate_manifest_roundtrip(tmp_path: Path) -> None:
    posts_path = tmp_path / "posts.json"
    posts_path.write_text(
        json.dumps(
            [{"id": 1, "theme": "T", "content": "C"}],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    polls_path = tmp_path / "polls.json"
    polls_path.write_text(
        json.dumps({"version": 1, "items": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    build_and_validate_manifest(
        base_dir=tmp_path,
        posts_path=posts_path,
        polls_path=polls_path,
    )
