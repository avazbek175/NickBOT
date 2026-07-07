import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.infrastructure.repository import UserRepository
from src.presentation.keyboards.inline import leaderboard_kb, back_kb

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "leaderboard")
async def show_leaderboard_menu(call: CallbackQuery, session: AsyncSession):
    repo = UserRepository(session)
    user = await repo.get(call.from_user.id)
    lang = user.language if user else __import__("src.domain.enums", fromlist=["Language"]).Language.UZBEK
    await call.message.edit_text(
        get_text("leaderboard_title", lang, list=get_text("generators_leaderboard", lang)),
        parse_mode="HTML",
        reply_markup=leaderboard_kb(lang),
    )
    await call.answer()


@router.callback_query(F.data.in_(["lb:gen", "lb:ref"]))
async def show_leaderboard(call: CallbackQuery, session: AsyncSession):
    mode = call.data.split(":")[1]
    repo = UserRepository(session)
    user = await repo.get(call.from_user.id)
    lang = user.language if user else __import__("src.domain.enums", fromlist=["Language"]).Language.UZBEK

    if mode == "gen":
        top = await repo.get_top_generators(10)
        title = get_text("generators_leaderboard", lang)
        lines = [f"{i+1}. @{u.username or u.id} — {u.total_generated}" for i, u in enumerate(top)]
    else:
        top = await repo.get_top_referrals(10)
        title = get_text("referrals_leaderboard", lang)
        lines = [f"{i+1}. @{u.username or u.id} — {u.referral_count}" for i, u in enumerate(top)]

    await call.message.edit_text(
        get_text("leaderboard_title", lang, list="\n".join(lines)),
        parse_mode="HTML",
        reply_markup=leaderboard_kb(lang),
    )
    await call.answer()
