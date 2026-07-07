import logging
import uuid
from typing import List, Optional
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.localizer import get_text
from src.domain.enums import Language
from src.infrastructure.repository import UserRepository, HistoryRepository
from src.services.user_service import UserService
from src.services.text_styler import TextStyler
from src.presentation.keyboards.inline import escape_html, back_kb

router = Router()
logger = logging.getLogger(__name__)


class StylerStates(StatesGroup):
    waiting_text = State()
    browsing = State()


STYLER_CATEGORIES = [
    ("fancy", "🎨 Fancy Fonts"),
    ("decorative", "👑 Decorative"),
    ("gaming", "⚡ Gaming"),
    ("invisible", "👻 Invisible"),
    ("symbols", "🔥 Symbols"),
    ("vip", "💎 VIP Style"),
    ("cute", "❤️ Cute"),
    ("dark", "😈 Dark"),
    ("hacker", "🤖 Hacker"),
    ("pubg", "🎮 PUBG"),
    ("glitch", "🌀 Glitch"),
    ("emoji", "⭐ Emoji Style"),
]

STYLER_CACHE: dict = {}
_MAX_CACHE = 300
PAGE_SIZE = 10


def _cache_styles(text: str, styles: List[tuple], category: str) -> str:
    token = uuid.uuid4().hex[:8]
    STYLER_CACHE[token] = {"text": text, "styles": styles, "category": category, "page": 1}
    if len(STYLER_CACHE) > _MAX_CACHE:
        keys = list(STYLER_CACHE.keys())
        for k in keys[:50]:
            del STYLER_CACHE[k]
    return token


def _get_cached(token: str) -> Optional[dict]:
    return STYLER_CACHE.get(token)


def styler_category_kb(lang: Language) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cid, cname in STYLER_CATEGORIES:
        builder.button(text=cname, callback_data=f"sc:{cid}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=get_text("back", lang), callback_data="bm"))
    return builder.as_markup()


def build_styler_results_kb(
    token: str, page: int, total_pages: int, lang: Language
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    cached = _get_cached(token)
    if not cached:
        return back_kb(lang)
    styles = cached["styles"]
    start = (page - 1) * PAGE_SIZE
    page_styles = styles[start:start + PAGE_SIZE]
    for i, (idx, style) in enumerate(page_styles):
        label = style[:30]
        builder.button(text=f"📋 {label}", callback_data=f"stcp:{token}:{start + i}")
    builder.adjust(2)
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀", callback_data=f"stp:{token}:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="▶", callback_data=f"stp:{token}:{page + 1}"))
    if nav:
        builder.row(*nav)
    builder.row(
        InlineKeyboardButton(text="🎲 New Text", callback_data="st:new"),
        InlineKeyboardButton(text="🏠 Menu", callback_data="bm"),
    )
    return builder.as_markup()


def build_copy_kb_styler(token: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ Back", callback_data=f"stbk:{token}")
    return builder.as_markup()


def format_styler_result(text: str, style: str, current: int, total: int, category: str) -> str:
    escaped = escape_html(style)
    return (
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>✨ Text Styler</b>\n"
        f"┌───────────────────\n"
        f"✏️ Original: <code>{escape_html(text)}</code>\n"
        f"│\n"
        f"{escaped}\n"
        f"└───────────────────\n"
        f"📂 {category}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )


async def get_lang(session: AsyncSession, user_id: int) -> Language:
    repo = UserRepository(session)
    user = await repo.get(user_id)
    return user.language if user else Language.UZBEK


def _build_styler_page_text(styles: List[tuple], page: int, cat: str) -> str:
    total = len(styles)
    start = (page - 1) * PAGE_SIZE
    page_styles = styles[start:start + PAGE_SIZE]
    numbers = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]
    lines = [
        "━━━━━━━━━━━━━━━━━━━━",
        f"<b>✨ {cat.title()} Style</b>",
        "┌───────────────────",
    ]
    for i, (_, s) in enumerate(page_styles):
        num = numbers[i] if i < len(numbers) else f"{i+1}."
        lines.append(f"{num} {escape_html(s)}")
    lines.append("└───────────────────")
    lines.append(f"📂 {cat.title()} — {total} styles")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


@router.message(F.text == "✨ Text Styler")
async def styler_start(message: Message, session: AsyncSession, state: FSMContext):
    lang = await get_lang(session, message.from_user.id)
    await state.set_state(StylerStates.waiting_text)
    await message.answer(
        "✍️ <b>Send any text or nickname.</b>\n\n"
        "Example: <code>Avazbek</code>, <code>PUBG</code>, <code>Shadow</code>",
        parse_mode="HTML",
        reply_markup=back_kb(lang),
    )


@router.callback_query(F.data == "st:new")
async def styler_new_text(call: CallbackQuery, state: FSMContext):
    await state.set_state(StylerStates.waiting_text)
    lang = Language.UZBEK
    await call.message.edit_text(
        "✍️ <b>Send any text or nickname.</b>\n\n"
        "Example: <code>Avazbek</code>, <code>PUBG</code>, <code>Shadow</code>",
        parse_mode="HTML",
        reply_markup=back_kb(lang),
    )
    await call.answer()


@router.message(StylerStates.waiting_text, F.text.len() >= 2)
async def styler_receive_text(message: Message, session: AsyncSession, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(session, user_id)
    text = message.text.strip()
    if not text or len(text) < 2:
        return

    user_service = UserService(session)
    await user_service.get_or_create(user_id, message.from_user.username,
                                      message.from_user.first_name, message.from_user.last_name)

    await state.update_data(input_text=text)
    await state.set_state(StylerStates.browsing)

    await message.answer(
        f"🎯 <b>Choose a style for:</b>\n\n<code>{escape_html(text)}</code>",
        parse_mode="HTML",
        reply_markup=styler_category_kb(lang),
    )


@router.callback_query(StylerStates.browsing, F.data.startswith("sc:"))
async def styler_category_selected(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    cat = parts[1]
    lang = await get_lang(session, call.from_user.id)
    user_id = call.from_user.id

    data = await state.get_data()
    orig_text = data.get("input_text")
    if not orig_text:
        logger.warning("FSM missing input_text for user %s in state %s", user_id, await state.get_state())
        await call.answer("Please send text first.", show_alert=True)
        return

    styles = _generate_styles(orig_text, cat)
    if not styles:
        await call.answer("No styles generated for this category.", show_alert=True)
        return

    total_pages = max(1, (len(styles) + PAGE_SIZE - 1) // PAGE_SIZE)
    indexed = [(i, s) for i, s in enumerate(styles)]
    token = _cache_styles(orig_text, indexed, cat)

    page_text = _build_styler_page_text(indexed, 1, cat)
    kb = build_styler_results_kb(token, 1, total_pages, lang)

    try:
        await call.message.edit_text(page_text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await call.message.answer(page_text, parse_mode="HTML", reply_markup=kb)
    await call.answer()

    hist_repo = HistoryRepository(session)
    for _, s in styles[:10]:
        await hist_repo.add(user_id, s, f"styler_{cat}")


def _generate_styles(text: str, category: str) -> List[str]:
    if category == "fancy":
        results = []
        seen = set()
        for name, style in TextStyler.get_all_font_styles(text):
            if style not in seen:
                results.append(style)
                seen.add(style)
        return results[:120]
    elif category == "decorative":
        return TextStyler.get_decorative_styles(text)[:120]
    elif category == "gaming":
        return TextStyler.get_gaming_styles(text)[:120]
    elif category == "invisible":
        return [TextStyler.invisible(text) for _ in range(10)]
    elif category == "symbols":
        results = []
        for sym in ["⚡", "★", "☆", "☠", "♛", "✿", "꧁", "꧂", "亗", "乂",
                     "メ", "ツ", "🔥", "💀", "🎯", "👑", "⭐", "🌙", "🌀", "♡"]:
            results.extend(TextStyler.get_symbol_variants(text, sym))
        return results[:120]
    elif category == "vip":
        return TextStyler.vip_style(text)[:120]
    elif category == "cute":
        return TextStyler.cute_style(text)[:120]
    elif category == "dark":
        return TextStyler.dark_style(text)[:120]
    elif category == "hacker":
        return [TextStyler.hacker_style(text) for _ in range(20)]
    elif category == "pubg":
        return TextStyler.pubg_style(text)[:120]
    elif category == "glitch":
        results = []
        for i in range(1, 6):
            for _ in range(5):
                results.append(TextStyler.glitch_text(text, i))
        return results[:120]
    elif category == "emoji":
        return TextStyler.get_emoji_styles(text)[:120]
    return []


@router.callback_query(StylerStates.browsing, F.data.startswith("stp:"))
async def styler_page(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    parts = call.data.split(":")
    if len(parts) < 3:
        await call.answer()
        return
    token = parts[1]
    try:
        page = int(parts[2])
    except (ValueError, IndexError):
        await call.answer()
        return

    lang = await get_lang(session, call.from_user.id)
    cached = _get_cached(token)
    if not cached:
        await call.answer("Session expired.", show_alert=True)
        return

    styles = cached["styles"]
    total_pages = max(1, (len(styles) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    cached["page"] = page
    cat = cached["category"]

    page_text = _build_styler_page_text(styles, page, cat)
    kb = build_styler_results_kb(token, page, total_pages, lang)

    try:
        await call.message.edit_text(page_text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        pass
    await call.answer()


@router.callback_query(StylerStates.browsing, F.data.startswith("stcp:"))
async def styler_copy(call: CallbackQuery, session: AsyncSession, state: FSMContext):
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

    lang = await get_lang(session, call.from_user.id)
    cached = _get_cached(token)
    if not cached or idx >= len(cached["styles"]):
        await call.answer("Style not found.", show_alert=True)
        return

    _, style = cached["styles"][idx]
    orig_text = cached["text"]
    cat = cached["category"]
    total = len(cached["styles"])

    text = format_styler_result(orig_text, style, idx + 1, total, cat)
    kb = build_copy_kb_styler(token)

    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        await call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()


@router.callback_query(StylerStates.browsing, F.data.startswith("stbk:"))
async def styler_back(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    parts = call.data.split(":")
    if len(parts) < 2:
        await call.answer()
        return
    token = parts[1]

    lang = await get_lang(session, call.from_user.id)
    cached = _get_cached(token)
    if not cached:
        await call.message.edit_text("Session expired.", reply_markup=back_kb(lang))
        await call.answer()
        return

    styles = cached["styles"]
    page = cached.get("page", 1)
    total_pages = max(1, (len(styles) + PAGE_SIZE - 1) // PAGE_SIZE)
    cat = cached["category"]

    page_text = _build_styler_page_text(styles, page, cat)
    kb = build_styler_results_kb(token, page, total_pages, lang)

    try:
        await call.message.edit_text(page_text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        pass
    await call.answer()
