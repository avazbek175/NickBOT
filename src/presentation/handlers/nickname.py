import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.enums import Language
from src.utils.localizer import get_text
from src.services.nickname_service import NicknameService
from src.services.user_service import UserService
from src.infrastructure.repository import UserRepository, FavoriteRepository, HistoryRepository
from src.presentation.keyboards.inline import (
    nickname_action_kb, nickname_list_action_kb, back_categories_kb, back_kb,
    random_count_kb,
)

router = Router()
logger = logging.getLogger(__name__)

CATEGORY_KEY_MAP = {
    "gaming": "🎮 Gaming",
    "premium": "👑 Premium",
    "cool": "🔥 Cool",
    "invisible": "👻 Invisible",
    "fancy_unicode": "⚡ Fancy Unicode",
    "decorated": "🎨 Decorated",
    "ai": "🤖 AI",
    "ai_gen": "🤖 AI",
    "hacker": "💀 Hacker",
    "king": "👑 King",
    "animal": "🐺 Animal",
    "anime": "🌌 Anime",
    "luxury": "💎 Luxury",
    "couple": "❤️ Couple",
    "cute": "🌸 Cute",
    "dark": "🌙 Dark",
    "space": "👽 Space",
    "robot": "⚙ Robot",
    "random": "🎲 Random",
}


async def get_lang(session: AsyncSession, user_id: int) -> Language:
    repo = UserRepository(session)
    user = await repo.get(user_id)
    return user.language if user else Language.UZBEK


@router.callback_query(F.data.startswith("cat:"))
async def category_selected(call: CallbackQuery, session: AsyncSession):
    cat = call.data.split(":")[1]
    lang = await get_lang(session, call.from_user.id)
    user_id = call.from_user.id

    if cat == "ai_gen":
        await call.message.edit_text(
            get_text("ai_prompt", lang),
            parse_mode="HTML",
            reply_markup=back_categories_kb(lang),
        )
        await call.answer()
        return

    nickname = NicknameService.generate_name(cat)
    category_name = CATEGORY_KEY_MAP.get(cat, cat)

    fav_repo = FavoriteRepository(session)
    is_fav = await fav_repo.exists(user_id, nickname)

    await call.message.edit_text(
        get_text("nickname_result", lang, nickname=nickname, category=category_name),
        parse_mode="HTML",
        reply_markup=nickname_action_kb(nickname, cat, is_fav, lang),
    )
    await call.answer()

    user_service = UserService(session)
    await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    await hist_repo.add(user_id, nickname, cat)


@router.message(F.text.len() > 3)
async def ai_nickname_handler(message: Message, session: AsyncSession):
    lang = await get_lang(session, message.from_user.id)
    text = message.text.strip()

    if text.startswith("/") or any(x in text for x in ["🏠", "✨", "🎮", "❤️", "📜", "🔍", "🎲", "👤", "🌐", "ℹ"]):
        return

    nickname = NicknameService.generate_ai_name()
    user_id = message.from_user.id
    fav_repo = FavoriteRepository(session)
    is_fav = await fav_repo.exists(user_id, nickname)

    await message.answer(
        get_text("nickname_result", lang, nickname=nickname, category="🤖 AI"),
        parse_mode="HTML",
        reply_markup=nickname_action_kb(nickname, "ai", is_fav, lang),
    )

    user_service = UserService(session)
    await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    await hist_repo.add(user_id, nickname, "ai")


@router.callback_query(F.data.startswith("gen_more:"))
async def generate_more(call: CallbackQuery, session: AsyncSession):
    cat = call.data.split(":")[1]
    lang = await get_lang(session, call.from_user.id)
    user_id = call.from_user.id

    nickname = NicknameService.generate_name(cat)
    category_name = CATEGORY_KEY_MAP.get(cat, cat)

    fav_repo = FavoriteRepository(session)
    is_fav = await fav_repo.exists(user_id, nickname)

    await call.message.edit_text(
        get_text("nickname_result", lang, nickname=nickname, category=category_name),
        parse_mode="HTML",
        reply_markup=nickname_action_kb(nickname, cat, is_fav, lang),
    )
    await call.answer()

    user_service = UserService(session)
    await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    await hist_repo.add(user_id, nickname, cat)


@router.callback_query(F.data.startswith("rand:"))
async def random_count(call: CallbackQuery, session: AsyncSession):
    count = int(call.data.split(":")[1])
    lang = await get_lang(session, call.from_user.id)
    user_id = call.from_user.id

    names = NicknameService.generate_multiple("random", count)
    lines = [f"{i+1}. `{n}`" for i, n in enumerate(names)]
    await call.message.edit_text(
        get_text("nickname_list", lang, list="\n".join(lines), category="🎲 Random"),
        parse_mode="HTML",
        reply_markup=nickname_list_action_kb("random", lang),
    )
    await call.answer()

    user_service = UserService(session)
    for _ in names:
        await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    for n in names:
        await hist_repo.add(user_id, n, "random")


@router.callback_query(F.data.startswith("copy:"))
async def copy_nickname(call: CallbackQuery):
    nickname = call.data.split(":", 1)[1]
    await call.answer(f"📋 {nickname}", show_alert=True)


@router.callback_query(F.data == "back_categories")
async def back_to_categories(call: CallbackQuery, session: AsyncSession):
    lang = await get_lang(session, call.from_user.id)
    from src.presentation.keyboards.inline import category_kb
    await call.message.edit_text(
        get_text("category_select", lang),
        parse_mode="HTML",
        reply_markup=category_kb(lang),
    )
    await call.answer()
