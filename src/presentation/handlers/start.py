import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.enums import Language, UserStatus
from src.utils.localizer import get_text
from src.presentation.keyboards.reply import main_menu_kb
from src.presentation.keyboards.inline import force_join_kb, back_kb
from src.services.user_service import UserService
from src.services.admin_service import AdminService
from src.infrastructure.repository import ForceChannelRepository
from src.config import config

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    referred_by = None
    if message.text and len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        if ref_code.startswith("ref_"):
            from src.infrastructure.repository import UserRepository
            repo = UserRepository(session)
            result = await session.execute(
                __import__("sqlalchemy").select(__import__("src.domain.models", fromlist=["User"]).User)
                .where(__import__("src.domain.models", fromlist=["User"]).User.referral_code == ref_code[4:])
            )
            referrer = result.scalar()
            if referrer:
                referred_by = referrer.id

    user_service = UserService(session)
    user = await user_service.get_or_create(user_id, username, first_name, last_name, referred_by)

    lang = user.language

    if config.force_join_enabled:
        force_repo = ForceChannelRepository(session)
        channels = await force_repo.get_active_channels()
        if channels:
            channel_list = [(ch.channel_title, ch.channel_link) for ch in channels]
            kb = force_join_kb(channel_list, lang)
            await message.answer(get_text("welcome_force", lang), reply_markup=kb, parse_mode="HTML")
            return

    stats = get_text("stats", lang, total_today=0, total_all=user.total_generated)
    await message.answer(
        get_text("welcome", lang),
        parse_mode="HTML",
    )
    await message.answer(
        get_text("main_menu", lang, name=first_name or username or str(user_id), stats=stats),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "check_subs")
async def check_subscriptions(call: CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    from src.infrastructure.repository import UserRepository
    repo = UserRepository(session)
    user = await repo.get(user_id)
    if not user:
        await call.answer(get_text("error", Language.UZBEK))
        return

    lang = user.language

    from src.infrastructure.repository import ForceChannelRepository
    force_repo = ForceChannelRepository(session)
    channels = await force_repo.get_active_channels()

    all_subscribed = True
    for ch in channels:
        try:
            member = await call.bot.get_chat_member(ch.channel_id, user_id)
            if member.status in ("left", "kicked", "restricted"):
                all_subscribed = False
                break
        except Exception:
            all_subscribed = False

    if all_subscribed:
        await repo.update(user_id, is_force_joined=True)
        stats = get_text("stats", lang, total_today=0, total_all=user.total_generated)
        await call.message.delete()
        await call.message.answer(get_text("sub_success", lang), parse_mode="HTML")
        await call.message.answer(
            get_text("main_menu", lang, name=user.first_name or user.username or str(user_id), stats=stats),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML",
        )
    else:
        await call.answer(get_text("sub_fail", lang), show_alert=True)


@router.message(Command("help"))
async def cmd_help(message: Message, session: AsyncSession):
    from src.infrastructure.repository import UserRepository
    repo = UserRepository(session)
    user = await repo.get(message.from_user.id)
    lang = user.language if user else Language.UZBEK
    await message.answer(get_text("help_text", lang), parse_mode="HTML", reply_markup=back_kb(lang))
