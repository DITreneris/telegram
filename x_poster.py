"""Optional X (Twitter) post: one image + short text via Tweepy (v1.1 media + v2 tweet)."""

from __future__ import annotations

import logging
from pathlib import Path

import tweepy

logger = logging.getLogger(__name__)

# Conservative limit for standard write access via API v2 (manifest hook may be up to 140).
MAX_POST_TEXT_CHARS = 280


def post_photo_with_caption(
    path: Path,
    text: str,
    *,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
) -> None:
    """Upload ``path`` and publish a post with ``text`` (caption). Raises on API errors."""
    body = text or ""
    if len(body) > MAX_POST_TEXT_CHARS:
        logger.warning(
            "Truncating X post text from %d to %d characters.",
            len(body),
            MAX_POST_TEXT_CHARS,
        )
        body = body[:MAX_POST_TEXT_CHARS]

    auth = tweepy.OAuth1UserHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    media = api_v1.media_upload(filename=str(path))
    media_id = media.media_id
    client_v2.create_tweet(text=body, media_ids=[media_id])
