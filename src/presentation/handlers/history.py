import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.infrastructure.repository import UserRepository, HistoryRepository
from src.presentation.keyboards.inline import back_kb

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "hist_clear")
async def clear_history(call: CallbackQuery, session: AsyncSession):
    user_id = call.from_user.id
    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else __import__("src.domain.enums", fromlist=["Language"]).Language.UZBEK

    hist_repo = HistoryRepository(session)
    await hist_repo.clear_user_history(user_id)

    await call.message.edit_text(
        get_text("history_cleared", lang),
        parse_mode="HTML",
        reply_markup=back_kb(lang),
    )
    await call.answer()
