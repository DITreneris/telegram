"""validate_config() su kontroliuojama aplinka (reload)."""

from __future__ import annotations

import importlib

import pytest


def _reload_config():
    import config as cfg

    importlib.reload(cfg)
    return cfg


@pytest.fixture(autouse=True)
def _restore_config_env(monkeypatch: pytest.MonkeyPatch):
    """Po kiekvieno testo — stabilios reikšmės kitiems testams."""
    monkeypatch.setenv("BOT_TOKEN", "pytest-dummy-token")
    monkeypatch.setenv("ADMIN_CHAT_ID", "123456789")
    yield
    _reload_config()


def test_validate_config_missing_bot_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    cfg = _reload_config()
    with pytest.raises(ValueError, match="BOT_TOKEN"):
        cfg.validate_config()


def test_validate_config_missing_admin_chat_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "")
    cfg = _reload_config()
    with pytest.raises(ValueError, match="ADMIN_CHAT_ID"):
        cfg.validate_config()


def test_validate_config_admin_not_integer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "not-an-int")
    cfg = _reload_config()
    with pytest.raises(ValueError, match="sveikasis"):
        cfg.validate_config()


def test_validate_config_admin_zero_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "0")
    cfg = _reload_config()
    with pytest.raises(ValueError, match="negali būti 0"):
        cfg.validate_config()


def test_validate_config_success_sets_admin_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "valid-token")
    monkeypatch.setenv("ADMIN_CHAT_ID", "987654321")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.ADMIN_CHAT_ID == 987654321
