"""Vercel serverless function to manage the bot webhook.

  GET  /setup                          → instructions page
  POST /setup                          → register webhook
  POST /setup?action=remove            → remove webhook

Requires BOT_TOKEN env var or send {"token": "..."} in POST body.
"""
import asyncio
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)


def handler(event, context):
    http_method = event.get("httpMethod", "GET")
    query = event.get("queryStringParameters") or {}
    body_raw = event.get("body") or ""

    bot_token = os.environ.get("BOT_TOKEN", "")
    vercel_url = os.environ.get("VERCEL_URL", "")
    webhook_url = f"https://{vercel_url}/webhook" if vercel_url else "https://<your-domain>.vercel.app/webhook"

    if http_method == "GET":
        html = f"""<html><body style="font-family:sans-serif;padding:2rem">
<h2>🔧 NickForge AI — Webhook Setup</h2>
<hr>
<h3>Set webhook</h3>
<pre>curl -X POST {webhook_url.replace('/webhook', '/setup')} \\
  -H "Content-Type: application/json" \\
  -d '{{"token": "YOUR_BOT_TOKEN"}}'</pre>

<h3>Remove webhook</h3>
<pre>curl -X POST "{webhook_url.replace('/webhook', '/setup')}?action=remove" \\
  -H "Content-Type: application/json" \\
  -d '{{"token": "YOUR_BOT_TOKEN"}}'</pre>

<h3>Check webhook</h3>
<pre>curl https://api.telegram.org/bot&lt;TOKEN&gt;/getWebhookInfo</pre>
<hr>
<p><small>Set <code>BOT_TOKEN</code> env in Vercel dashboard to auto-auth.</small></p>
</body></html>"""
        return {
            "statusCode": 200,
            "body": html,
            "headers": {"Content-Type": "text/html; charset=utf-8"},
        }

    # POST
    action = query.get("action", "set")

    if not bot_token:
        try:
            data = json.loads(body_raw)
            bot_token = data.get("token", "")
        except Exception:
            pass

    if not bot_token:
        return {"statusCode": 400, "body": "Missing BOT_TOKEN", "headers": {"Content-Type": "text/plain"}}

    async def run():
        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        try:
            if action == "remove":
                await bot.delete_webhook(drop_pending_updates=True)
                return "✅ Webhook removed"
            else:
                result = await bot.set_webhook(
                    url=webhook_url,
                    drop_pending_updates=True,
                    allowed_updates=[
                        "message", "edited_message", "callback_query",
                        "inline_query", "my_chat_member", "chat_member",
                    ],
                )
                info = await bot.get_webhook_info()
                if result:
                    return f"✅ Webhook set!\nURL: {info.url}\nPending: {info.pending_update_count}"
                return f"❌ Failed. Info: {info}"
        finally:
            await bot.session.close()

    loop = _get_loop()
    result = loop.run_until_complete(run())

    return {"statusCode": 200, "body": result, "headers": {"Content-Type": "text/plain; charset=utf-8"}}


def _get_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
