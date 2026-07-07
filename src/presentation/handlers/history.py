import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.domain.enums import Language
from src.infrastructure.repository import UserRepository, HistoryRepository
from src.services.user_service import UserService
from src.presentation.keyboards.inline import back_kb

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "hc")
async def clear_history(call: CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    user_service = UserService(session)
    user = await user_service.get_or_create(
        user_id,
        call.from_user.username,
        call.from_user.first_name,
        call.from_user.last_name,
    )
    lang = user.language

    hist_repo = HistoryRepository(session)
    await hist_repo.clear_user_history(user_id)

    await call.message.edit_text(
        get_text("history_cleared", lang),
        parse_mode="HTML",
        reply_markup=back_kb(lang),
    )
    await call.answer()
