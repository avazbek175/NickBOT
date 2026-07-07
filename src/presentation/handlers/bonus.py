import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.services.user_service import UserService
from src.presentation.keyboards.inline import back_kb

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "db")
async def claim_daily_bonus(call: CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    user_service = UserService(session)
    user = await user_service.get_or_create(
        user_id,
        call.from_user.username,
        call.from_user.first_name,
        call.from_user.last_name,
    )
    lang = user.language

    available, remaining = await user_service.daily_bonus_available(user_id)
    if available:
        coins = await user_service.claim_daily_bonus(user_id)
        await call.answer(f"🎁 +{coins} coins!", show_alert=True)
        user = await user_service.get_or_create(
            user_id,
            call.from_user.username,
            call.from_user.first_name,
            call.from_user.last_name,
        )
        await call.message.edit_text(
            get_text("daily_bonus_text", lang, coins=coins, balance=user.coins),
            parse_mode="HTML",
            reply_markup=back_kb(lang),
        )
    else:
        hours = (remaining or 0) // 3600
        minutes = ((remaining or 0) % 3600) // 60
        await call.answer(
            get_text("daily_claimed", lang, time=f"{hours}h {minutes}m"),
            show_alert=True,
        )
