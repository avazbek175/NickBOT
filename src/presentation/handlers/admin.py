import logging
import traceback
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


async def _ensure_admin(
    user_id: int, event: Message | CallbackQuery, lang: Language
) -> bool:
    if user_id in config.admin_id_list:
        return True
    text = "❌ You are not an administrator."
    if isinstance(event, Message):
        await event.answer(text)
    elif isinstance(event, CallbackQuery):
        await event.answer(text, show_alert=True)
    logger.warning("Admin access denied for user %s", user_id)
    return False


async def _get_lang(session: AsyncSession, user_id: int) -> Language:
    repo = UserRepository(session)
    user = await repo.get(user_id)
    return user.language if user else Language.UZBEK


@router.message(Command("admin"))
async def admin_panel(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    lang = await _get_lang(session, user_id)
    if not await _ensure_admin(user_id, message, lang):
        return

    logger.info("Admin %s opened admin panel", user_id)
    try:
        await message.answer(
            get_text("admin_panel", lang),
            reply_markup=admin_main_kb(lang),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Error opening admin panel for %s", user_id)
        await message.answer(get_text("error", lang))


ADMIN_BUTTON_PREFIXES = [
    "📊 Admin Dashboard",
    "📊 Statistika",
    "📊 Админ",
    "👥 Users",
    "👥 Foydalanuvchilar",
    "👥 Пользователи",
    "📢 Broadcast",
    "📢 Рассылка",
    "➕ Add Channel",
    "➕ Kanal qo'shish",
    "➕ Добавить канал",
    "➖ Remove Channel",
    "➖ Kanal olib tashlash",
    "➖ Удалить канал",
    "📈 Statistics",
    "📈 Statistika",
    "📈 Статистика",
    "⚙ Settings",
    "⚙ Sozlamalar",
    "⚙ Настройки",
    "🎁 Daily",
    "🎁 Kundalik",
    "🎁 Ежедневный",
    "🎯 Referral",
    "🎯 Referal",
    "🎯 Реферал",
    "📝 Logs",
    "📝 Loglar",
    "📝 Логи",
    "🚫 Ban",
    "🚫 Bloklash",
    "🚫 Заблокировать",
    "✅ Unban",
    "✅ Разблокировать",
    "🔍 Find",
    "🔍 Foydalanuvchini",
    "🔍 Найти",
    "📂 Export",
    "📂 Экспорт",
]


@router.message(F.text.func(lambda t: any(t.startswith(p) for p in ADMIN_BUTTON_PREFIXES)))
async def admin_text_handler(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    lang = await _get_lang(session, user_id)
    if not await _ensure_admin(user_id, message, lang):
        return

    text = message.text
    admin_service = AdminService(session)
    repo = UserRepository(session)

    try:
        if "📊" in text and ("Admin" in text or "Stat" in text or "Админ" in text or "Statistika" in text):
            logger.info("Admin %s opened dashboard", user_id)
            dashboard = await admin_service.get_dashboard()
            await message.answer(
                get_text("admin_dashboard", lang, **dashboard),
                parse_mode="HTML",
                reply_markup=admin_dashboard_kb(lang),
            )

        elif "👥" in text or "Foydalanuvchilar" in text or "Пользователи" in text or "Users" in text:
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            total = await repo.count()
            today = await repo.count(and_(UserModel.created_at >= today_start))
            banned = await repo.count(UserModel.status == UserStatus.BANNED)
            body = (
                f"👥 <b>{get_text('users', lang)}</b>\n\n"
                f"{get_text('statistics', lang)}:\n"
                f"Total: <b>{total}</b>\n"
                f"Today: <b>{today}</b>\n"
                f"Banned: <b>{banned}</b>"
            )
            await message.answer(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif "📢" in text or "Broadcast" in text or "Рассылка" in text:
            logger.info("Admin %s opened broadcast", user_id)
            body = "📢 <b>Broadcast</b>\n\nSend a message to forward to all users.\n\nSupported: Text, Photo, Video, Animation, Document, Voice, Audio, Sticker"
            await message.answer(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif "➕" in text or "Add" in text or "Kanal qo" in text or "Добавить" in text:
            body = "➕ <b>Add Force Channel</b>\n\nSend: <code>channel_id | title | link</code>"
            await message.answer(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif "➖" in text or ("Remove" in text) or ("Udalit" in text) or ("olib tashlash" in text):
            force_repo = ForceChannelRepository(session)
            channels = await force_repo.get_all()
            if not channels:
                body = "No channels configured."
            else:
                lines = [f"{ch.id}. {ch.channel_title} ({'✅' if ch.is_active else '❌'})" for ch in channels]
                body = "Channels:\n\n" + "\n".join(lines) + "\n\nSend ID to remove."
            await message.answer(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif "⚙" in text or "Settings" in text or "Sozlamalar" in text or "Настройки" in text:
            logger.info("Admin %s opened settings", user_id)
            settings = await admin_service.get_settings()
            body = get_text("bot_settings", lang, settings="\n".join(f"{k}: {v}" for k, v in settings.items()) if settings else "No custom settings")
            await message.answer(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif "🚫" in text or "Ban" in text or "Bloklash" in text or "Заблокировать" in text:
            body = "🚫 Send user ID to ban:"
            await message.answer(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif "✅" in text or "Unban" in text or "Разблокировать" in text:
            body = "✅ Send user ID to unban:"
            await message.answer(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif "🔍" in text or "Find" in text or "Найти" in text or "Foydalanuvchini" in text:
            body = "🔍 Send username or ID to find:"
            await message.answer(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif "📂" in text or "Export" in text or "Экспорт" in text:
            body = "📂 Export feature coming soon."
            await message.answer(body, parse_mode="HTML", reply_markup=back_kb(lang))

        else:
            dashboard = await admin_service.get_dashboard()
            await message.answer(
                get_text("admin_dashboard", lang, **dashboard),
                parse_mode="HTML",
                reply_markup=admin_dashboard_kb(lang),
            )
    except Exception:
        logger.exception("Admin text handler error for %s: %s", user_id, text)
        await message.answer(get_text("error", lang))


@router.callback_query(F.data.startswith("a"))
async def admin_callback_handler(call: CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    lang = await _get_lang(session, user_id)
    if not await _ensure_admin(user_id, call, lang):
        return

    action = call.data
    repo = UserRepository(session)

    try:
        if action == "ast":
            logger.info("Admin %s opened statistics", user_id)
            admin_service = AdminService(session)
            dashboard = await admin_service.get_dashboard()
            await call.message.edit_text(
                get_text("admin_dashboard", lang, **dashboard),
                parse_mode="HTML",
                reply_markup=admin_dashboard_kb(lang),
            )

        elif action == "au":
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            total = await repo.count()
            today = await repo.count(and_(UserModel.created_at >= today_start))
            banned = await repo.count(UserModel.status == UserStatus.BANNED)
            body = (
                f"👥 <b>{get_text('users', lang)}</b>\n\n"
                f"Total: <b>{total}</b>\n"
                f"Today: <b>{today}</b>\n"
                f"Banned: <b>{banned}</b>"
            )
            await call.message.edit_text(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif action == "abr":
            logger.info("Admin %s opened broadcast", user_id)
            body = "📢 <b>Broadcast</b>\n\nSend a message to forward to all users."
            await call.message.edit_text(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif action == "aac":
            body = "➕ <b>Add Force Channel</b>\n\nSend: <code>channel_id | title | link</code>"
            await call.message.edit_text(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif action == "arc":
            force_repo = ForceChannelRepository(session)
            channels = await force_repo.get_all()
            if not channels:
                body = "No channels configured."
            else:
                lines = [f"{ch.id}. {ch.channel_title} ({'✅' if ch.is_active else '❌'})" for ch in channels]
                body = "Channels:\n\n" + "\n".join(lines) + "\n\nSend ID to remove."
            await call.message.edit_text(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif action == "aset":
            logger.info("Admin %s opened settings", user_id)
            admin_service = AdminService(session)
            settings = await admin_service.get_settings()
            body = get_text("bot_settings", lang, settings="\n".join(f"{k}: {v}" for k, v in settings.items()) if settings else "No custom settings")
            await call.message.edit_text(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif action == "aban":
            body = "🚫 Send user ID to ban:"
            await call.message.edit_text(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif action == "aunb":
            body = "✅ Send user ID to unban:"
            await call.message.edit_text(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif action == "afind":
            body = "🔍 Send username or ID to find:"
            await call.message.edit_text(body, parse_mode="HTML", reply_markup=back_kb(lang))

        elif action == "aexp":
            body = "📂 Export feature coming soon."
            await call.message.edit_text(body, parse_mode="HTML", reply_markup=back_kb(lang))

        await call.answer()
    except Exception:
        logger.exception("Admin callback error for %s action=%s", user_id, action)
        try:
            await call.answer(get_text("error", lang), show_alert=True)
        except Exception:
            pass


@router.message(F.text.startswith("📢"))
async def broadcast_text_handler(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    lang = await _get_lang(session, user_id)
    if not await _ensure_admin(user_id, message, lang):
        return

    try:
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
            logger.info("Admin %s completed broadcast %s (success=%s fail=%s)", user_id, bc.id, bc.success_count, bc.fail_count)
            await message.answer(f"✅ Broadcast completed!\nSuccess: {bc.success_count}\nFailed: {bc.fail_count}")
    except Exception:
        logger.exception("Broadcast error for admin %s", user_id)
        await message.answer(get_text("error", lang))
