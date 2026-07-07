import logging
import uuid
from typing import List, Dict, Optional
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.enums import Language
from src.utils.localizer import get_text
from src.services.nickname_service import NicknameService
from src.services.user_service import UserService
from src.infrastructure.repository import UserRepository, FavoriteRepository, HistoryRepository
from src.presentation.keyboards.inline import (
    build_nicknames_kb,
    build_copy_kb,
    copy_message_text,
    back_categories_kb,
    back_kb,
    category_kb,
    random_count_kb,
)

router = Router()
logger = logging.getLogger(__name__)

PAGE_SIZE = 10

# In-memory page cache: token -> {"names": [...], "category": str}
_page_cache: Dict[str, dict] = {}
_MAX_CACHE = 500


async def get_lang(session: AsyncSession, user_id: int) -> Language:
    repo = UserRepository(session)
    user = await repo.get(user_id)
    return user.language if user else Language.UZBEK


def _cache_names(names: List[str], category: str) -> str:
    token = uuid.uuid4().hex[:8]
    _page_cache[token] = {"names": names, "category": category}
    if len(_page_cache) > _MAX_CACHE:
        keys = list(_page_cache.keys())
        for k in keys[:100]:
            del _page_cache[k]
    return token


def _get_cached(token: str) -> Optional[dict]:
    return _page_cache.get(token)


def _compute_pages(total: int) -> int:
    return max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)


@router.callback_query(F.data.startswith("cat:"))
async def category_selected(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    cat = parts[1]
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

    names = NicknameService.generate_multiple(cat, PAGE_SIZE)
    if not names:
        names = NicknameService.generate_multiple("random", PAGE_SIZE)

    token = _cache_names(names, cat)
    text, kb = build_nicknames_kb(names, token, cat, 1, 1, lang)

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()

    user_service = UserService(session)
    for _ in names:
        await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    for n in names:
        await hist_repo.add(user_id, n, cat)


@router.message(F.text.len() > 3)
async def ai_nickname_handler(message: Message, session: AsyncSession):
    text = message.text.strip()
    if text.startswith("/") or any(x in text for x in ["🏠", "✨", "🎮", "❤️", "📜", "🔍", "🎲", "👤", "🌐", "ℹ"]):
        return

    lang = await get_lang(session, message.from_user.id)
    user_id = message.from_user.id

    names = [NicknameService.generate_ai_name() for _ in range(PAGE_SIZE)]
    token = _cache_names(names, "ai")
    text, kb = build_nicknames_kb(names, token, "ai", 1, 1, lang)

    await message.answer(text, parse_mode="HTML", reply_markup=kb)

    user_service = UserService(session)
    for _ in names:
        await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    for n in names:
        await hist_repo.add(user_id, n, "ai")


@router.callback_query(F.data.startswith("ga:"))
async def generate_again(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    cat = parts[1]
    lang = await get_lang(session, call.from_user.id)
    user_id = call.from_user.id

    names = NicknameService.generate_multiple(cat, PAGE_SIZE)
    token = _cache_names(names, cat)
    text, kb = build_nicknames_kb(names, token, cat, 1, 1, lang)

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()

    user_service = UserService(session)
    for _ in names:
        await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    for n in names:
        await hist_repo.add(user_id, n, cat)


@router.callback_query(F.data.startswith("pn:"))
async def page_next(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 3:
        await call.answer()
        return
    cat = parts[1]
    old_token = parts[2]
    lang = await get_lang(session, call.from_user.id)
    user_id = call.from_user.id

    old_data = _get_cached(old_token)
    old_page = old_data.get("page", 1) if isinstance(old_data, dict) else 1
    new_page = old_page + 1

    names = NicknameService.generate_multiple(cat, PAGE_SIZE)
    token = _cache_names(names, cat)
    cached = _get_cached(token)
    if cached:
        cached["page"] = new_page

    total_pages = new_page
    text, kb = build_nicknames_kb(names, token, cat, new_page, total_pages, lang)

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()

    user_service = UserService(session)
    for _ in names:
        await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    for n in names:
        await hist_repo.add(user_id, n, cat)


@router.callback_query(F.data.startswith("pp:"))
async def page_prev(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 3:
        await call.answer()
        return
    cat = parts[1]
    old_token = parts[2]
    lang = await get_lang(session, call.from_user.id)
    user_id = call.from_user.id

    old_data = _get_cached(old_token)
    old_page = old_data.get("page", 2) if isinstance(old_data, dict) else 2
    prev_page = max(1, old_page - 1)

    names = NicknameService.generate_multiple(cat, PAGE_SIZE)
    token = _cache_names(names, cat)
    cached = _get_cached(token)
    if cached:
        cached["page"] = prev_page

    total_pages = old_page
    text, kb = build_nicknames_kb(names, token, cat, prev_page, total_pages, lang)

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()

    user_service = UserService(session)
    for _ in names:
        await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    for n in names:
        await hist_repo.add(user_id, n, cat)


@router.callback_query(F.data.startswith("r:"))
async def random_count(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    try:
        count = int(parts[1])
    except (ValueError, IndexError):
        await call.answer()
        return
    lang = await get_lang(session, call.from_user.id)
    user_id = call.from_user.id

    all_names = NicknameService.generate_multiple("random", count)
    page_1_names = all_names[:PAGE_SIZE]
    total_pages = _compute_pages(count)

    token = _cache_names(all_names, "random")
    cached = _get_cached(token)
    if cached:
        cached["page"] = 1
        cached["total_pages"] = total_pages

    text, kb = build_nicknames_kb(page_1_names, token, "random", 1, total_pages, lang)

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()

    user_service = UserService(session)
    for _ in all_names:
        await user_service.increment_generated(user_id)

    hist_repo = HistoryRepository(session)
    for n in all_names:
        await hist_repo.add(user_id, n, "random")


@router.callback_query(F.data.startswith("n:"))
async def copy_nickname(call: CallbackQuery):
    parts = call.data.split(":")
    if len(parts) < 3:
        await call.answer()
        return
    token = parts[1]
    try:
        idx = int(parts[2])
    except (ValueError, IndexError):
        await call.answer()
        return

    cached = _get_cached(token)
    if cached and idx < len(cached["names"]):
        name = cached["names"][idx]
    else:
        cat = cached.get("category", "random") if cached else "random"
        name = NicknameService.generate_name(cat)

    text = copy_message_text(name)
    await call.message.answer(text, parse_mode="HTML", reply_markup=build_copy_kb(name, token, Language.UZBEK))
    await call.answer()


@router.callback_query(F.data.startswith("bk:"))
async def back_from_copy(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    token = parts[1]
    lang = await get_lang(session, call.from_user.id)

    cached = _get_cached(token)
    if cached:
        names = cached.get("names", [])
        cat = cached.get("category", "random")
        page = cached.get("page", 1)
        total_pages = cached.get("total_pages", 1)
        text, kb = build_nicknames_kb(names[:PAGE_SIZE], token, cat, page, total_pages, lang)
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await call.message.delete()
        await call.message.answer("Session expired. Please generate again.", reply_markup=back_kb(lang))

    await call.answer()


@router.callback_query(F.data == "bc")
async def back_to_categories(call: CallbackQuery, session: AsyncSession):
    lang = await get_lang(session, call.from_user.id)
    await call.message.edit_text(
        get_text("category_select", lang),
        parse_mode="HTML",
        reply_markup=category_kb(lang),
    )
    await call.answer()


@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery):
    await call.answer()
