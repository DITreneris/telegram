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
    with pytest.raises(ValueError, match="integer"):
        cfg.validate_config()


def test_validate_config_admin_zero_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "0")
    cfg = _reload_config()
    with pytest.raises(ValueError, match="cannot be 0"):
        cfg.validate_config()


def test_validate_config_success_sets_admin_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "valid-token")
    monkeypatch.setenv("ADMIN_CHAT_ID", "987654321")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.ADMIN_CHAT_ID == 987654321


def test_validate_config_scheduled_posting_sets_timezone_and_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Empty target must win over .env so default falls back to ADMIN_CHAT_ID.
    monkeypatch.setenv("SCHEDULE_TARGET_CHAT_ID", "")
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "111")
    monkeypatch.setenv("ENABLE_SCHEDULED_POSTING", "true")
    monkeypatch.setenv("SCHEDULE_TZ", "Europe/Vilnius")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.ENABLE_SCHEDULED_POSTING is True
    assert cfg.SCHEDULE_TIMEZONE is not None
    assert cfg.SCHEDULE_TIMEZONE.key == "Europe/Vilnius"
    assert cfg.SCHEDULE_TARGET_CHAT_ID == 111
    assert cfg.SCHEDULE_NOTIFY_ON_FAILURE is True


def test_validate_config_schedule_notify_on_failure_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "111")
    monkeypatch.setenv("ENABLE_SCHEDULED_POSTING", "true")
    monkeypatch.setenv("SCHEDULE_TZ", "Europe/Vilnius")
    monkeypatch.setenv("SCHEDULE_NOTIFY_ON_FAILURE", "false")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.SCHEDULE_NOTIFY_ON_FAILURE is False


def test_validate_config_scheduled_custom_target_chat(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "111")
    monkeypatch.setenv("ENABLE_SCHEDULED_POSTING", "1")
    monkeypatch.setenv("SCHEDULE_TARGET_CHAT_ID", "-1001234567890")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.SCHEDULE_TARGET_CHAT_ID == -1001234567890


def test_validate_config_schedule_tz_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    monkeypatch.setenv("ENABLE_SCHEDULED_POSTING", "true")
    monkeypatch.setenv("SCHEDULE_TZ", "NotA/Real_Zone")
    cfg = _reload_config()
    with pytest.raises(ValueError, match="SCHEDULE_TZ"):
        cfg.validate_config()


def test_validate_config_schedule_target_zero_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    monkeypatch.setenv("ENABLE_SCHEDULED_POSTING", "true")
    monkeypatch.setenv("SCHEDULE_TARGET_CHAT_ID", "0")
    cfg = _reload_config()
    with pytest.raises(ValueError, match="SCHEDULE_TARGET_CHAT_ID"):
        cfg.validate_config()


def test_validate_config_x_posting_requires_twitter_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    monkeypatch.setenv("ENABLE_X_POSTING", "true")
    monkeypatch.delenv("TWITTER_API_KEY", raising=False)
    monkeypatch.delenv("TWITTER_API_SECRET", raising=False)
    monkeypatch.delenv("TWITTER_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("TWITTER_ACCESS_TOKEN_SECRET", raising=False)
    cfg = _reload_config()
    with pytest.raises(ValueError, match="TWITTER_API_KEY"):
        cfg.validate_config()


def test_validate_config_x_posting_ok_sets_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    monkeypatch.setenv("ENABLE_X_POSTING", "1")
    monkeypatch.setenv("TWITTER_API_KEY", "k")
    monkeypatch.setenv("TWITTER_API_SECRET", "ks")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "t")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN_SECRET", "ts")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.ENABLE_X_POSTING is True
    assert cfg.TWITTER_API_KEY == "k"
    assert cfg.TWITTER_API_SECRET == "ks"
    assert cfg.TWITTER_ACCESS_TOKEN == "t"
    assert cfg.TWITTER_ACCESS_TOKEN_SECRET == "ts"
    assert cfg.X_NOTIFY_ON_FAILURE is True


def test_validate_config_queue_state_path_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("QUEUE_STATE_PATH", raising=False)
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.STATE_PATH == (cfg.BASE_DIR / "data" / "state.json").resolve()


def test_validate_config_queue_state_path_absolute(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    target = tmp_path / "vol" / "state.json"
    monkeypatch.setenv("QUEUE_STATE_PATH", str(target))
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.STATE_PATH == target.resolve()


def test_validate_config_queue_state_path_relative_to_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QUEUE_STATE_PATH", "data/state_railway_test.json")
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.STATE_PATH == (cfg.BASE_DIR / "data" / "state_railway_test.json").resolve()


def test_validate_config_x_notify_on_failure_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("ADMIN_CHAT_ID", "1")
    monkeypatch.setenv("ENABLE_X_POSTING", "true")
    monkeypatch.setenv("TWITTER_API_KEY", "k")
    monkeypatch.setenv("TWITTER_API_SECRET", "ks")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "t")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN_SECRET", "ts")
    monkeypatch.setenv("X_NOTIFY_ON_FAILURE", "false")
    cfg = _reload_config()
    cfg.validate_config()
    assert cfg.X_NOTIFY_ON_FAILURE is False
