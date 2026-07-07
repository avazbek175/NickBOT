import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.domain.enums import Language
from src.infrastructure.repository import UserRepository
from src.services.user_service import UserService
from src.presentation.keyboards.inline import leaderboard_kb, back_kb

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "lb")
async def show_leaderboard_menu(call: CallbackQuery, session: AsyncSession):
    user_service = UserService(session)
    user = await user_service.get_or_create(
        call.from_user.id,
        call.from_user.username,
        call.from_user.first_name,
        call.from_user.last_name,
    )
    lang = user.language
    await call.message.edit_text(
        get_text("leaderboard_title", lang, list=get_text("generators_leaderboard", lang)),
        parse_mode="HTML",
        reply_markup=leaderboard_kb(lang),
    )
    await call.answer()


@router.callback_query(F.data.in_(["lb:gen", "lb:ref"]))
async def show_leaderboard(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    mode = parts[1]
    repo = UserRepository(session)
    user_service = UserService(session)
    user = await user_service.get_or_create(
        call.from_user.id,
        call.from_user.username,
        call.from_user.first_name,
        call.from_user.last_name,
    )
    lang = user.language

    if mode == "gen":
        top = await repo.get_top_generators(10)
        lines = [f"{i+1}. @{u.username or u.id} — {u.total_generated}" for i, u in enumerate(top)]
    else:
        top = await repo.get_top_referrals(10)
        lines = [f"{i+1}. @{u.username or u.id} — {u.referral_count}" for i, u in enumerate(top)]

    await call.message.edit_text(
        get_text("leaderboard_title", lang, list="\n".join(lines)),
        parse_mode="HTML",
        reply_markup=leaderboard_kb(lang),
    )
    await call.answer()
