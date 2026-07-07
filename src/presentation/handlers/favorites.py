import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.domain.enums import Language
from src.infrastructure.repository import FavoriteRepository, UserRepository
from src.services.user_service import UserService
from src.presentation.keyboards.inline import favorites_kb, back_kb

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("fa:"))
async def add_favorite(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":", 2)
    if len(parts) < 3:
        await call.answer()
        return
    nickname = parts[1]
    category = parts[2]
    user_id = call.from_user.id

    user_service = UserService(session)
    user = await user_service.get_or_create(
        user_id,
        call.from_user.username,
        call.from_user.first_name,
        call.from_user.last_name,
    )
    lang = user.language

    fav_repo = FavoriteRepository(session)
    exists = await fav_repo.exists(user_id, nickname)
    if exists:
        await call.answer(get_text("already_saved", lang), show_alert=True)
        return

    await fav_repo.add(user_id, nickname, category)
    user.favorites_count += 1
    await session.commit()

    await call.answer(get_text("saved", lang, nickname=nickname), show_alert=True)


@router.callback_query(F.data.startswith("sa:"))
async def save_all_favorites(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 3:
        await call.answer()
        return
    token = parts[1]
    category = parts[2]
    user_id = call.from_user.id

    from src.presentation.handlers.nickname import _get_cached
    cached = _get_cached(token)

    if not cached:
        await call.answer("Session expired. Generate again.", show_alert=True)
        return

    user_service = UserService(session)
    user = await user_service.get_or_create(
        user_id,
        call.from_user.username,
        call.from_user.first_name,
        call.from_user.last_name,
    )
    lang = user.language

    fav_repo = FavoriteRepository(session)
    saved_count = 0
    for name in cached["names"]:
        exists = await fav_repo.exists(user_id, name)
        if not exists:
            await fav_repo.add(user_id, name, category)
            user.favorites_count += 1
            saved_count += 1

    await session.commit()
    await call.answer(f"⭐ {saved_count} nicknames saved!", show_alert=True)


@router.callback_query(F.data.startswith("fd:"))
async def remove_favorite_by_id(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    try:
        fid = int(parts[1])
    except (ValueError, IndexError):
        await call.answer()
        return
    user_id = call.from_user.id

    user_service = UserService(session)
    user = await user_service.get_or_create(
        user_id,
        call.from_user.username,
        call.from_user.first_name,
        call.from_user.last_name,
    )
    lang = user.language

    fav_repo = FavoriteRepository(session)
    await fav_repo.delete(fid)
    user.favorites_count = max(0, user.favorites_count - 1)
    await session.commit()

    await call.answer(get_text("deleted", lang), show_alert=True)
    favs = await fav_repo.get_user_favorites(user_id)
    if not favs:
        await call.message.edit_text(get_text("favorites_empty", lang), parse_mode="HTML", reply_markup=back_kb(lang))
        return
    total = await fav_repo.count(user_id)
    total_pages = max(1, (total + 9) // 10)
    kb = favorites_kb([(f.id, f.nickname) for f in favs], 0, total_pages, lang)
    await call.message.edit_text(
        get_text("favorites_list", lang, list="\n".join(f"{i+1}. `{f.nickname}`" for i, f in enumerate(favs))),
        parse_mode="HTML",
        reply_markup=kb,
    )


@router.callback_query(F.data.startswith("fp:"))
async def favorites_pagination(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    try:
        page = int(parts[1])
    except (ValueError, IndexError):
        await call.answer()
        return
    user_id = call.from_user.id

    user_service = UserService(session)
    user = await user_service.get_or_create(
        user_id,
        call.from_user.username,
        call.from_user.first_name,
        call.from_user.last_name,
    )
    lang = user.language

    fav_repo = FavoriteRepository(session)
    favs = await fav_repo.get_user_favorites(user_id, page * 10, 10)
    total = await fav_repo.count(user_id)
    total_pages = max(1, (total + 9) // 10)

    lines = [f"{i+1}. `{f.nickname}`" for i, f in enumerate(favs)]
    kb = favorites_kb([(f.id, f.nickname) for f in favs], page, total_pages, lang)
    await call.message.edit_text(
        get_text("favorites_list", lang, list="\n".join(lines)),
        parse_mode="HTML",
        reply_markup=kb,
    )
    await call.answer()
