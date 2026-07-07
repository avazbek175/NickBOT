import logging
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.enums import Language
from src.utils.localizer import get_text
from src.services.nickname_service import NicknameService
from src.infrastructure.repository import UserRepository
from src.presentation.keyboards.inline import back_kb

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text.len() >= 2)
async def search_handler(message: Message, session: AsyncSession):
    query = message.text.strip()
    if query.startswith("/"):
        return

    repo = UserRepository(session)
    user = await repo.get(message.from_user.id)
    if not user:
        return
    lang = user.language

    if any(x in query for x in ["🏠", "✨", "🎮", "❤️", "📜", "🔍", "🎲", "👤", "🌐", "ℹ"]):
        return

    results = NicknameService.search(query)
    if not results:
        await message.answer(
            get_text("search_empty", lang),
            parse_mode="HTML",
            reply_markup=back_kb(lang),
        )
        return

    lines = [f"`{n}`" for n in results]
    await message.answer(
        get_text("search_results", lang, query=query, list="\n".join(lines)),
        parse_mode="HTML",
        reply_markup=back_kb(lang),
    )
