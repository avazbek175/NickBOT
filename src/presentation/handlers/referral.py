import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.services.user_service import UserService
from src.infrastructure.repository import UserRepository
from src.config import config

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "referral")
async def show_referral(call: CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else __import__("src.domain.enums", fromlist=["Language"]).Language.UZBEK

    user_service = UserService(session)
    link = await user_service.get_referral_link(user_id)

    await call.message.edit_text(
        get_text("referral_text", lang, link=link, count=user.referral_count, coins=config.referral_coins),
        parse_mode="HTML",
        reply_markup=__import__("src.presentation.keyboards.inline", fromlist=["back_kb"]).back_kb(lang),
    )
    await call.answer()
