import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.services.user_service import UserService
from src.presentation.keyboards.inline import back_kb
from src.config import config

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "ref")
async def show_referral(call: CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    user_service = UserService(session)
    user = await user_service.get_or_create(
        user_id,
        call.from_user.username,
        call.from_user.first_name,
        call.from_user.last_name,
    )
    lang = user.language
    link = await user_service.get_referral_link(user_id)

    await call.message.edit_text(
        get_text("referral_text", lang, link=link, count=user.referral_count, coins=config.referral_coins),
        parse_mode="HTML",
        reply_markup=back_kb(lang),
    )
    await call.answer()
