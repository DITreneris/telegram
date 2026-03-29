"""Turinio eilė pagal last_delivered_id + hook būsimam grafikui."""

from __future__ import annotations

from pathlib import Path

from content_loader import load_content
from schemas import ContentItem, ContentManifest
from state_store import load as load_state
from state_store import save_atomic


async def schedule_next_delivery(delay_seconds: float | None = None) -> None:
    """Rezervuota: APScheduler / cron / išorinis trigger. MVP nenaudojama."""
    del delay_seconds


class Orchestrator:
    def __init__(self, *, content_path: Path, state_path: Path, base_dir: Path) -> None:
        self._content_path = content_path
        self._state_path = state_path
        self._base_dir = base_dir

    def load_manifest(self) -> ContentManifest:
        return load_content(self._content_path, base_dir=self._base_dir)

    @staticmethod
    def _next_after(items: tuple[ContentItem, ...], last_id: str | None) -> ContentItem:
        if not items:
            raise ValueError("Content list is empty.")
        if last_id is None:
            return items[0]
        idxs = [i for i, it in enumerate(items) if it.id == last_id]
        if not idxs:
            return items[0]
        return items[(idxs[0] + 1) % len(items)]

    def peek_next_item(self) -> ContentItem:
        manifest = self.load_manifest()
        state = load_state(self._state_path)
        return self._next_after(manifest.items, state.get("last_delivered_id"))

    def record_delivered(self, item_id: str) -> None:
        state = load_state(self._state_path)
        state["last_delivered_id"] = item_id
        save_atomic(self._state_path, state)

    def status_text(self) -> str:
        manifest = self.load_manifest()
        state = load_state(self._state_path)
        last = state.get("last_delivered_id")
        return (
            f"Items: {len(manifest.items)}\n"
            f"Last delivered id: {last!r}\n"
            f"Updated: {state.get('updated_at')!r}"
        )
