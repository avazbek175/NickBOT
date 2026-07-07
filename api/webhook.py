"""
Vercel serverless function for Telegram bot webhook.

  POST /webhook  →  processes Telegram Update, returns 200 OK

Uses module-level singletons from src.bot for cold-start efficiency.
"""
import asyncio
import json
import logging
import os
import sys
from http import HTTPStatus

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from aiogram.types import Update
from src import bot as app_bot
from src.config import config
from src.infrastructure.cache import init_redis
from src.infrastructure.database import get_session

logger = logging.getLogger(__name__)

_initialized = False


async def _ensure_init():
    global _initialized
    if _initialized:
        return

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    try:
        await init_redis()
    except Exception as e:
        logger.warning("Redis unavailable (non-fatal): %s", e)

    _initialized = True
    logger.info("Webhook handler ready | bot=%s", config.bot_name)


# ── Vercel Python Runtime entry point ─────────────────────────────────
def handler(event, context):
    """Vercel Python Runtime wraps this as WSGI.

    event: dict with 'httpMethod', 'path', 'body', 'headers', etc.
    """
    http_method = event.get("httpMethod", "GET")
    body_raw = event.get("body", "") or ""
    headers = event.get("headers", {})

    if http_method != "POST":
        return {
            "statusCode": 200,
            "body": "OK",
            "headers": {"Content-Type": "text/plain"},
        }

    try:
        data = json.loads(body_raw) if body_raw else {}
    except json.JSONDecodeError:
        logger.warning("Invalid JSON body")
        return {"statusCode": 400, "body": "Invalid JSON"}

    async def _process():
        await _ensure_init()
        update = Update.model_validate(data)
        dp = app_bot.get_dispatcher()
        bot = app_bot.get_bot()
        await dp.feed_update(bot, update, session_getter=get_session)

    loop = _get_or_create_loop()
    try:
        loop.run_until_complete(_process())
    except Exception as e:
        logger.exception("Webhook processing error: %s", e)
        return {"statusCode": 500, "body": "Error"}

    return {
        "statusCode": 200,
        "body": "OK",
        "headers": {"Content-Type": "text/plain"},
    }


def _get_or_create_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
