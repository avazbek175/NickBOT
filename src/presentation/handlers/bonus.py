import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.services.user_service import UserService
from src.infrastructure.repository import UserRepository

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "daily_bonus")
async def claim_daily_bonus(call: CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    user_service = UserService(session)
    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else __import__("src.domain.enums", fromlist=["Language"]).Language.UZBEK

    available, remaining = await user_service.daily_bonus_available(user_id)
    if available:
        coins = await user_service.claim_daily_bonus(user_id)
        await call.answer(f"🎁 +{coins} coins!", show_alert=True)
        user = await repo.get(user_id)
        await call.message.edit_text(
            get_text("daily_bonus_text", lang, coins=coins, balance=user.coins),
            parse_mode="HTML",
            reply_markup=__import__("src.presentation.keyboards.inline", fromlist=["back_kb"]).back_kb(lang),
        )
    else:
        from datetime import timedelta
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        await call.answer(
            get_text("daily_claimed", lang, time=f"{hours}h {minutes}m"),
            show_alert=True,
        )
