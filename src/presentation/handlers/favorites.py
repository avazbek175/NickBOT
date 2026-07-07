import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.infrastructure.repository import FavoriteRepository, UserRepository
from src.presentation.keyboards.inline import favorites_kb, back_kb

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("fav_add:"))
async def add_favorite(call: CallbackQuery, session: AsyncSession):
    parts = call.data.split(":", 2)
    nickname = parts[1]
    category = parts[2]
    user_id = call.from_user.id

    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else __import__("src.domain.enums", fromlist=["Language"]).Language.UZBEK

    fav_repo = FavoriteRepository(session)
    exists = await fav_repo.exists(user_id, nickname)
    if exists:
        await call.answer(get_text("already_saved", lang), show_alert=True)
        return

    await fav_repo.add(user_id, nickname, category)
    user.favorites_count += 1
    await session.commit()

    await call.answer(get_text("saved", lang, nickname=nickname), show_alert=True)
    from src.presentation.keyboards.inline import nickname_action_kb
    await call.message.edit_reply_markup(
        reply_markup=nickname_action_kb(nickname, category, True, lang)
    )


@router.callback_query(F.data.startswith("fav_del:"))
async def remove_favorite(call: CallbackQuery, session: AsyncSession):
    nickname = call.data.split(":", 1)[1]
    user_id = call.from_user.id

    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else __import__("src.domain.enums", fromlist=["Language"]).Language.UZBEK

    fav_repo = FavoriteRepository(session)
    favs = await fav_repo.get_user_favorites(user_id)
    for fav in favs:
        if fav.nickname == nickname:
            await fav_repo.delete(fav.id)
            user.favorites_count = max(0, user.favorites_count - 1)
            await session.commit()
            break

    await call.answer(get_text("deleted", lang), show_alert=True)


@router.callback_query(F.data.startswith("fav_del_id:"))
async def remove_favorite_by_id(call: CallbackQuery, session: AsyncSession):
    fid = int(call.data.split(":")[1])
    user_id = call.from_user.id

    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else __import__("src.domain.enums", fromlist=["Language"]).Language.UZBEK

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


@router.callback_query(F.data.startswith("fav_page:"))
async def favorites_pagination(call: CallbackQuery, session: AsyncSession):
    page = int(call.data.split(":")[1])
    user_id = call.from_user.id

    repo = UserRepository(session)
    user = await repo.get(user_id)
    lang = user.language if user else __import__("src.domain.enums", fromlist=["Language"]).Language.UZBEK

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
