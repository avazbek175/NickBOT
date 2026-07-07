"""Vercel Python runtime entrypoint.

Only stdlib imports at module level so Vercel's build scanner
can parse this file before installing dependencies.
"""
import json
import os
import sys


def handler(event, context):
    """Vercel Python Serverless Function handler."""
    method = event.get("httpMethod", "GET")
    path = (event.get("path") or event.get("rawPath", "/")).rstrip("/")
    body_raw = event.get("body", "") or ""
    headers = event.get("headers", {})

    # ── Lazy init: import heavy deps only at runtime ──────────────
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))

    if path == "/setup" or path == "":
        return _handle_setup(method, body_raw)

    return _handle_webhook(method, body_raw)


def _handle_setup(method, body_raw):
    """GET → HTML instructions; POST → register webhook."""
    if method == "GET":
        vercel_url = os.environ.get("VERCEL_URL", "")
        wh_url = f"https://{vercel_url}/webhook" if vercel_url else "https://<domain>/webhook"
        html = f"""<html><body style="font-family:sans-serif;padding:2rem">
<h2>🔧 NickForge AI — Webhook Setup</h2>
<form method="post">
<button type="submit">Set Webhook → {wh_url}</button>
</form>
</body></html>"""
        return {"statusCode": 200, "body": html, "headers": {"Content-Type": "text/html; charset=utf-8"}}

    bot_token = os.environ.get("BOT_TOKEN", "")
    if not bot_token and body_raw:
        try:
            bot_token = json.loads(body_raw).get("token", "")
        except Exception:
            pass

    if not bot_token:
        return {"statusCode": 400, "body": "BOT_TOKEN not set"}

    import asyncio
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties

    async def run():
        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode="HTML"))
        vercel_url = os.environ.get("VERCEL_URL", "")
        webhook_url = f"https://{vercel_url}/webhook" if vercel_url else "https://<domain>/webhook"
        result = await bot.set_webhook(url=webhook_url, drop_pending_updates=True,
                                       allowed_updates=["message", "edited_message",
                                                        "callback_query", "inline_query",
                                                        "my_chat_member", "chat_member"])
        info = await bot.get_webhook_info()
        await bot.session.close()
        return f"Webhook: {'✅' if result else '❌'}\nURL: {info.url}\nPending: {info.pending_update_count}"

    loop = _get_loop()
    result = loop.run_until_complete(run())
    return {"statusCode": 200, "body": result, "headers": {"Content-Type": "text/plain; charset=utf-8"}}


def _handle_webhook(method, body_raw):
    """POST /webhook → process Telegram Update."""
    if method != "POST":
        return {"statusCode": 200, "body": "OK", "headers": {"Content-Type": "text/plain"}}

    import asyncio
    import logging
    from aiogram.types import Update
    from src import bot as app_bot
    from src.config import config
    from src.infrastructure.cache import init_redis

    logging.basicConfig(level=getattr(logging, config.log_level.upper(), logging.INFO))

    try:
        data = json.loads(body_raw) if body_raw else {}
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": "Invalid JSON"}

    async def _process():
        try:
            await init_redis()
        except Exception:
            pass
        update = Update.model_validate(data)
        dp = app_bot.get_dispatcher()
        bot = app_bot.get_bot()
        await dp.feed_update(bot, update)

    loop = _get_loop()
    try:
        loop.run_until_complete(_process())
    except Exception as e:
        logging.getLogger(__name__).exception("Webhook error: %s", e)
        return {"statusCode": 500, "body": "Error"}

    return {"statusCode": 200, "body": "OK", "headers": {"Content-Type": "text/plain"}}


def _get_loop():
    import asyncio
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
