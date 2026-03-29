"""resolve_log_level() elgsena."""

from __future__ import annotations

import logging
import warnings

import pytest

from config import resolve_log_level


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
        ("debug", logging.DEBUG),
    ],
)
def test_resolve_log_level_valid(monkeypatch: pytest.MonkeyPatch, value: str, expected: int) -> None:
    monkeypatch.setenv("LOG_LEVEL", value)
    assert resolve_log_level() == expected


def test_resolve_log_level_default_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    assert resolve_log_level() == logging.INFO


def test_resolve_log_level_invalid_falls_back_to_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "VERBOSE")
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        assert resolve_log_level() == logging.INFO
    assert len(rec) == 1
    assert issubclass(rec[0].category, UserWarning)
