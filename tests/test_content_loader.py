"""content_loader FileNotFound ir įkėlimas."""

from __future__ import annotations

from pathlib import Path

import pytest

from content_loader import load_content


def test_load_content_missing_file_raises(tmp_path: Path) -> None:
    path = tmp_path / "no_such_content.json"
    with pytest.raises(FileNotFoundError, match="Turinio failas nerastas"):
        load_content(path, base_dir=tmp_path)
