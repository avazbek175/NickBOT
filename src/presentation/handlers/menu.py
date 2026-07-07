import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.enums import Language
from src.utils.localizer import get_text
from src.presentation.keyboards.reply import main_menu_kb
from src.presentation.keyboards.inline import (
    category_kb, back_kb, language_kb, profile_kb,
    leaderboard_kb, random_count_kb,
)
from src.services.user_service import UserService
from src.infrastructure.repository import UserRepository, FavoriteRepository, HistoryRepository

router = Router()
logger = logging.getLogger(__name__)


async def get_user_lang(session: AsyncSession, user_id: int) -> Language:
    repo = UserRepository(session)
    user = await repo.get(user_id)
    return user.language if user else Language.UZBEK


@router.message(F.text.in_(["🏠 Bosh menyu", "🏠 Home", "🏠 Главная"]))
async def go_home_text(message: Message, session: AsyncSession):
    await show_home(message, session)


@router.callback_query(F.data == "bm")
async def go_home_callback(call: CallbackQuery, session: AsyncSession):
    await call.answer()
    try:
        await call.message.delete()
    except Exception:
        pass
    await show_home(call.message, session)


async def show_home(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    user_service = UserService(session)
    user = await user_service.get_or_create(
        user_id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )
    lang = user.language
    stats = get_text("stats", lang, total_today=0, total_all=user.total_generated)
    await message.answer(
        get_text("main_menu", lang, name=user.first_name or user.username or str(user_id), stats=stats),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML",
    )


@router.message(F.text.func(lambda t: any(t.startswith(x) for x in ["✨", "🎮", "❤️", "📜", "🔍", "🎲", "👤", "🌐", "ℹ"])))
async def menu_handler(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    lang = await get_user_lang(session, user_id)
    user_service = UserService(session)
    text = message.text

    if "✨" in text:
        await show_categories(message, lang)
    elif "🎮" in text:
        await show_categories(message, lang)
    elif "❤️" in text:
        await show_favorites(message, session, lang)
    elif "📜" in text:
        await show_history(message, session, lang)
    elif "🔍" in text:
        await message.answer(get_text("search_prompt", lang), parse_mode="HTML", reply_markup=back_kb(lang))
    elif "🎲" in text:
        await message.answer(get_text("random_count", lang), parse_mode="HTML", reply_markup=random_count_kb(lang))
    elif "👤" in text:
        await show_profile(message, session, lang, user_service)
    elif "🌐" in text:
        await message.answer(get_text("lang_select", lang), parse_mode="HTML", reply_markup=language_kb())
    elif "ℹ" in text:
        await message.answer(get_text("help_text", lang), parse_mode="HTML", reply_markup=back_kb(lang))


async def show_categories(message: Message, lang: Language):
    await message.answer(
        get_text("category_select", lang),
        reply_markup=category_kb(lang),
        parse_mode="HTML",
    )


async def show_favorites(message: Message, session: AsyncSession, lang: Language):
    user_id = message.from_user.id
    fav_repo = FavoriteRepository(session)
    favs = await fav_repo.get_user_favorites(user_id, 0, 10)
    if not favs:
        await message.answer(get_text("favorites_empty", lang), parse_mode="HTML", reply_markup=back_kb(lang))
        return
    lines = [f"{i+1}. `{f.nickname}`" for i, f in enumerate(favs)]
    from src.presentation.keyboards.inline import favorites_kb
    kb = favorites_kb([(f.id, f.nickname) for f in favs], 0, 1, lang)
    await message.answer(
        get_text("favorites_list", lang, list="\n".join(lines)),
        parse_mode="HTML",
        reply_markup=kb,
    )


async def show_history(message: Message, session: AsyncSession, lang: Language):
    user_id = message.from_user.id
    hist_repo = HistoryRepository(session)
    entries = await hist_repo.get_user_history(user_id, 0, 10)
    if not entries:
        await message.answer(get_text("history_empty", lang), parse_mode="HTML", reply_markup=back_kb(lang))
        return
    lines = [f"{i+1}. `{e.nickname}` — {e.category}" for i, e in enumerate(entries)]
    await message.answer(
        get_text("history_list", lang, list="\n".join(lines)),
        parse_mode="HTML",
        reply_markup=back_kb(lang),
    )


async def show_profile(message: Message, session: AsyncSession, lang: Language, user_service: UserService = None):
    user_id = message.from_user.id
    if not user_service:
        user_service = UserService(session)
    data = await user_service.get_profile_data(user_id)
    if not data:
        await message.answer(get_text("error", lang))
        return
    data["lang"] = lang.value.upper()
    from src.domain.enums import Language as LangEnum
    lang_map = {LangEnum.UZBEK: "🇺🇿", LangEnum.ENGLISH: "🇺🇸", LangEnum.RUSSIAN: "🇷🇺"}
    data["lang"] = f"{lang_map.get(lang, '')} {lang.value.upper()}"
    await message.answer(
        get_text("profile_text", lang, **data),
        parse_mode="HTML",
        reply_markup=profile_kb(lang),
    )
