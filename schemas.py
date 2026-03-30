"""Minimalūs turinio modeliai ir validacija (be papildomų priklausomybių)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

ContentType = Literal["text", "photo", "document"]

# Hook text shared with Telegram media caption and future short-form channels (e.g. X/Twitter).
MAX_CAPTION_CHARS = 140


@dataclass(frozen=True)
class ContentItem:
    id: str
    type: ContentType
    text: str | None = None
    path: str | None = None
    caption: str | None = None


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
        if ctype not in ("text", "photo", "document"):
            raise ValueError(f'Item "{item_id}": type turi būti text | photo | document.')

        text = _optional_str(row, "text")
        path_raw = _optional_str(row, "path")
        caption = _optional_str(row, "caption")

        if ctype == "text":
            if not text:
                raise ValueError(f'Item "{item_id}" (text): reikia lauko "text".')
            if path_raw:
                raise ValueError(f'Item "{item_id}" (text): neturėtų būti "path".')
            out.append(ContentItem(id=item_id, type="text", text=text, caption=None))
        else:
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
                )
            )

    return ContentManifest(version=1, items=tuple(out))
