"""Minimalūs turinio modeliai ir validacija (be papildomų priklausomybių)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

ContentType = Literal["text", "photo", "document", "poll"]

# Hook text shared with Telegram media caption and future short-form channels (e.g. X/Twitter).
MAX_CAPTION_CHARS = 140

# Telegram Bot API sendMessage body limit (also used for poll debrief `theme_note`).
MAX_MESSAGE_CHARS = 4096

# Telegram Bot API poll limits (sendPoll).
MAX_POLL_QUESTION_CHARS = 300
MAX_POLL_OPTION_CHARS = 100
MIN_POLL_OPTIONS = 2
MAX_POLL_OPTIONS = 10


@dataclass(frozen=True)
class ContentItem:
    id: str
    type: ContentType
    text: str | None = None
    path: str | None = None
    caption: str | None = None
    poll_question: str | None = None
    poll_options: tuple[str, ...] | None = None
    poll_correct_option_id: int | None = None
    related_post_id: int | None = None
    theme_note: str | None = None


@dataclass(frozen=True)
class ContentManifest:
    version: int
    items: tuple[ContentItem, ...]


def _require_str(obj: dict[str, Any], key: str, *, item_id: str) -> str:
    v = obj.get(key)
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f'Item "{item_id}": laukas "{key}" turi būti ne tuščia eilutė.')
    return v.strip()


def _optional_str(obj: dict[str, Any], key: str) -> str | None:
    v = obj.get(key)
    if v is None:
        return None
    if not isinstance(v, str):
        raise ValueError(f'Laukas "{key}" turi būti eilutė arba nebūti.')
    s = v.strip()
    return s or None


def _optional_related_post_id(obj: dict[str, Any], *, item_id: str) -> int | None:
    v = obj.get("related_post_id")
    if v is None:
        return None
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f'Item "{item_id}": "related_post_id" turi būti sveikasis skaičius arba nebūti.')
    if v < 1:
        raise ValueError(f'Item "{item_id}": "related_post_id" turi būti >= 1.')
    return v


def _optional_theme_note(obj: dict[str, Any], *, item_id: str) -> str | None:
    v = obj.get("theme_note")
    if v is None:
        return None
    if not isinstance(v, str):
        raise ValueError(f'Item "{item_id}": "theme_note" turi būti eilutė arba nebūti.')
    s = v.strip()
    return s or None


def _parse_poll_options(raw: object, *, item_id: str) -> tuple[str, ...]:
    if not isinstance(raw, list):
        raise ValueError(f'Item "{item_id}" (poll): "options" turi būti sąrašas.')
    if not MIN_POLL_OPTIONS <= len(raw) <= MAX_POLL_OPTIONS:
        raise ValueError(
            f'Item "{item_id}" (poll): "options" turi turėti nuo {MIN_POLL_OPTIONS} iki '
            f"{MAX_POLL_OPTIONS} elementų."
        )
    out: list[str] = []
    for i, el in enumerate(raw):
        if not isinstance(el, str) or not el.strip():
            raise ValueError(f'Item "{item_id}" (poll): options[{i}] turi būti ne tuščia eilutė.')
        s = el.strip()
        if len(s) > MAX_POLL_OPTION_CHARS:
            raise ValueError(
                f'Item "{item_id}" (poll): options[{i}] ilgis negali viršyti '
                f"{MAX_POLL_OPTION_CHARS} simbolių."
            )
        out.append(s)
    return tuple(out)


def parse_manifest(raw: dict[str, Any], *, base_dir: Path) -> ContentManifest:
    if not isinstance(raw, dict):
        raise ValueError("content.json šaknis turi būti objektas.")
    ver = raw.get("version")
    if ver != 1:
        raise ValueError('Laukas "version" turi būti 1.')
    items_raw = raw.get("items")
    if not isinstance(items_raw, list) or not items_raw:
        raise ValueError('"items" turi būti ne tuščias sąrašas.')

    seen: set[str] = set()
    out: list[ContentItem] = []
    for i, row in enumerate(items_raw):
        if not isinstance(row, dict):
            raise ValueError(f"items[{i}] turi būti objektas.")
        item_id = _require_str(row, "id", item_id=f"#{i}")
        if item_id in seen:
            raise ValueError(f'Dubliuotas item id: "{item_id}".')
        seen.add(item_id)
        ctype = row.get("type")
        if ctype not in ("text", "photo", "document", "poll"):
            raise ValueError(
                f'Item "{item_id}": type turi būti text | photo | document | poll.'
            )

        related_post_id = _optional_related_post_id(row, item_id=item_id)
        theme_note = _optional_theme_note(row, item_id=item_id)

        text = _optional_str(row, "text")
        path_raw = _optional_str(row, "path")
        caption = _optional_str(row, "caption")

        if ctype == "text":
            if not text:
                raise ValueError(f'Item "{item_id}" (text): reikia lauko "text".')
            if path_raw:
                raise ValueError(f'Item "{item_id}" (text): neturėtų būti "path".')
            out.append(
                ContentItem(
                    id=item_id,
                    type="text",
                    text=text,
                    caption=None,
                    related_post_id=related_post_id,
                    theme_note=theme_note,
                )
            )
            continue

        if ctype == "poll":
            if text or path_raw or caption:
                raise ValueError(f'Item "{item_id}" (poll): neturėtų būti "text", "path" arba "caption".')
            q = _require_str(row, "question", item_id=item_id)
            if len(q) > MAX_POLL_QUESTION_CHARS:
                raise ValueError(
                    f'Item "{item_id}" (poll): "question" ilgis negali viršyti '
                    f"{MAX_POLL_QUESTION_CHARS} simbolių."
                )
            opts = _parse_poll_options(row.get("options"), item_id=item_id)
            cid = row.get("correct_option_id")
            if isinstance(cid, bool) or not isinstance(cid, int):
                raise ValueError(
                    f'Item "{item_id}" (poll): reikia sveikojo "correct_option_id" (0 … n-1).'
                )
            if not 0 <= cid < len(opts):
                raise ValueError(
                    f'Item "{item_id}" (poll): "correct_option_id" turi būti tarp 0 ir {len(opts) - 1}.'
                )
            if theme_note is not None and len(theme_note) > MAX_MESSAGE_CHARS:
                raise ValueError(
                    f'Item "{item_id}" (poll): "theme_note" negali būti ilgesnis nei '
                    f"{MAX_MESSAGE_CHARS} simbolių (dabar {len(theme_note)})."
                )
            out.append(
                ContentItem(
                    id=item_id,
                    type="poll",
                    poll_question=q,
                    poll_options=opts,
                    poll_correct_option_id=cid,
                    related_post_id=related_post_id,
                    theme_note=theme_note,
                )
            )
            continue

        if not path_raw:
            raise ValueError(f'Item "{item_id}" ({ctype}): reikia lauko "path".')
        root = base_dir.resolve()
        p = (base_dir / path_raw).resolve()
        if p != root and root not in p.parents:
            raise ValueError(f'Item "{item_id}": kelias turi būti po projekto šaknimi.')
        if not p.is_file():
            raise ValueError(f'Item "{item_id}": failas nerastas: {p}')
        if caption is not None and len(caption) > MAX_CAPTION_CHARS:
            raise ValueError(
                f'Item "{item_id}" ({ctype}): laukas "caption" negali būti ilgesnis nei '
                f"{MAX_CAPTION_CHARS} simbolių (dabar {len(caption)})."
            )
        out.append(
            ContentItem(
                id=item_id,
                type=ctype,  # type: ignore[arg-type]
                text=None,
                path=str(p),
                caption=caption,
                related_post_id=related_post_id,
                theme_note=theme_note,
            )
        )

    return ContentManifest(version=1, items=tuple(out))
