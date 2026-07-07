import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.enums import Language, UserStatus
from src.domain.models import User as UserModel
from src.utils.localizer import get_text
from src.services.admin_service import AdminService
from src.services.user_service import UserService
from src.infrastructure.repository import UserRepository, ForceChannelRepository, BroadcastRepository
from src.presentation.keyboards.reply import admin_main_kb, main_menu_kb
from src.presentation.keyboards.inline import admin_dashboard_kb, back_kb
from src.config import config

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("admin"))
async def admin_panel(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    if user_id not in config.admin_id_list:
        return

    admin_service = AdminService(session)
    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else Language.UZBEK

    await message.answer(
        get_text("admin_panel", lang),
        reply_markup=admin_main_kb(lang),
        parse_mode="HTML",
    )


@router.message(F.text == "📊 Admin Dashboard")
async def admin_dashboard_handler(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    if user_id not in config.admin_id_list:
        return

    admin_service = AdminService(session)
    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else Language.UZBEK

    dashboard = await admin_service.get_dashboard()
    text = get_text("admin_dashboard", lang, **dashboard)

    await message.answer(text, parse_mode="HTML", reply_markup=admin_dashboard_kb(lang))


@router.callback_query(F.data.startswith("a"))
async def admin_callback_handler(call: CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    if user_id not in config.admin_id_list:
        await call.answer("Access denied")
        return

    action = call.data
    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else Language.UZBEK

    if action == "ast":
        admin_service = AdminService(session)
        dashboard = await admin_service.get_dashboard()
        text = get_text("admin_dashboard", lang, **dashboard)
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=admin_dashboard_kb(lang))

    elif action == "au":
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        total = await repo.count()
        today = await repo.count(
            and_(
                UserModel.created_at >= today_start
            )
        )
        text = (
            f"👥 <b>Users</b>\n\n"
            f"Total: {total}\n"
            f"Today: {today}\n"
            f"Banned: {await repo.count(UserModel.status == UserStatus.BANNED)}"
        )
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang))

    elif action == "abr":
        text = "📢 <b>Broadcast</b>\n\nSend a message to forward to all users.\n\nSupported: Text, Photo, Video, Animation, Document, Voice, Audio, Sticker"
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang))

    elif action == "aac":
        text = "➕ <b>Add Force Channel</b>\n\nSend: <code>channel_id | title | link</code>"
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang))

    elif action == "arc":
        force_repo = ForceChannelRepository(session)
        channels = await force_repo.get_all()
        if not channels:
            text = "No channels configured."
        else:
            lines = [f"{ch.id}. {ch.channel_title} ({'✅' if ch.is_active else '❌'})" for ch in channels]
            text = "Channels:\n\n" + "\n".join(lines) + "\n\nSend ID to remove."
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang))

    elif action == "aset":
        admin_service = AdminService(session)
        settings = await admin_service.get_settings()
        text = get_text("bot_settings", lang, settings="\n".join(f"{k}: {v}" for k, v in settings.items()) if settings else "No custom settings")
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang))

    elif action == "aban":
        text = "🚫 Send user ID to ban:"
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang))

    elif action == "aunb":
        text = "✅ Send user ID to unban:"
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang))

    elif action == "afind":
        text = "🔍 Send username or ID to find:"
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang))

    elif action == "aexp":
        text = "📂 Export feature coming soon."
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang))

    await call.answer()


@router.message(F.text.startswith("📢"))
async def broadcast_text_handler(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    if user_id not in config.admin_id_list:
        return

    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else Language.UZBEK

    if message.text and len(message.text) > 10:
        bc_repo = BroadcastRepository(session)
        bc = await bc_repo.create(
            admin_id=user_id,
            broadcast_type="text",
            content=message.text,
        )

        from src.services.broadcast_service import BroadcastService
        bcs = BroadcastService(session, message.bot)
        await message.answer("⏳ Broadcasting...")
        await bcs.start_broadcast(bc.id, message)
        await message.answer(f"✅ Broadcast completed!\nSuccess: {bc.success_count}\nFailed: {bc.fail_count}")
