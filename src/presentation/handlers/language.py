import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.enums import Language
from src.utils.localizer import get_text
from src.infrastructure.repository import UserRepository
from src.presentation.keyboards.reply import main_menu_kb

router = Router()
logger = logging.getLogger(__name__)

LANG_NAMES = {
    "uz": "🇺🇿 O'zbek",
    "en": "🇺🇸 English",
    "ru": "🇷🇺 Русский",
}


@router.callback_query(F.data.startswith("l:"))
async def change_language(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    lang_code = parts[1]
    new_lang = Language(lang_code)

    repo = UserRepository(session)
    user = await repo.get(call.from_user.id)
    if user:
        await repo.update(call.from_user.id, language=new_lang)

    await call.message.delete()
    await call.message.answer(
        get_text("lang_changed", new_lang, lang=LANG_NAMES.get(lang_code, lang_code)),
        parse_mode="HTML",
        reply_markup=main_menu_kb(new_lang),
    )
    await call.answer()
