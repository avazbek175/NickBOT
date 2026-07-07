from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional, Tuple
from src.utils.localizer import get_text
from src.domain.enums import Language


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def category_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    categories = [
        ("gaming", t("gaming")),
        ("premium", t("premium")),
        ("cool", t("cool")),
        ("invisible", t("invisible")),
        ("fancy", t("fancy")),
        ("decorated", t("decorated")),
        ("ai_gen", t("ai_gen")),
        ("hacker", t("hacker")),
        ("king", t("king")),
        ("animal", t("animal")),
        ("anime", t("anime")),
        ("luxury", t("luxury")),
        ("couple", t("couple")),
        ("cute", t("cute")),
        ("dark", t("dark")),
        ("space", t("space")),
        ("robot", t("robot")),
        ("random", t("random")),
    ]
    for cid, cname in categories:
        builder.button(text=cname, callback_data=f"cat:{cid}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="bm"))
    return builder.as_markup()


def build_nicknames_kb(
    names: List[str],
    token: str,
    category: str,
    page: int,
    total_pages: int,
    lang: Language = Language.UZBEK,
) -> Tuple[str, InlineKeyboardMarkup]:
    t = lambda k: get_text(k, lang)
    numbers = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]
    cat_name = CATEGORY_DISPLAY.get(category, category)

    lines = ["━━━━━━━━━━━━━━━━━━━━"]
    lines.append(f"<b>{cat_name}</b>")
    lines.append("┌───────────────────")
    for i, name in enumerate(names[:10]):
        num = numbers[i] if i < len(numbers) else f"{i+1}."
        lines.append(f"{num} {escape_html(name)}")
    lines.append("└───────────────────")
    lines.append(f"📂 Category: {cat_name}")
    lines.append("━━━━━━━━━━━━━━━━━━━━")

    text = "\n".join(lines)

    builder = InlineKeyboardBuilder()
    for i, name in enumerate(names[:10]):
        builder.button(text=f"📋 {name[:20]}", callback_data=f"n:{token}:{i}")

    builder.adjust(2)

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀", callback_data=f"pp:{category}:{token}"))
    nav_text = f"📄 {page}/{total_pages}"
    nav_row.append(InlineKeyboardButton(text=nav_text, callback_data="noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="▶", callback_data=f"pn:{category}:{token}"))
    builder.row(*nav_row)

    builder.row(
        InlineKeyboardButton(text="🎲 Generate Again", callback_data=f"ga:{category}"),
        InlineKeyboardButton(text="❤️ Save All", callback_data=f"sa:{token}:{category}"),
    )
    builder.row(InlineKeyboardButton(text="🏠 Main Menu", callback_data="bm"))

    return text, builder.as_markup()


def build_copy_kb(name: str, token: str, lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ Back", callback_data=f"bk:{token}")
    return builder.as_markup()


def copy_message_text(name: str) -> str:
    escaped = escape_html(name)
    return (
        "━━━━━━━━━━━━━━━\n"
        "📋 <b>Ready to Copy</b>\n\n"
        f"<code>{escaped}</code>\n\n"
        "Tap and hold to copy.\n"
        "━━━━━━━━━━━━━━━"
    )


def favorites_kb(favs: List[Tuple[int, str]], page: int, total_pages: int, lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    for fid, nickname in favs:
        builder.button(text=f"🗑 {nickname[:20]}", callback_data=f"fd:{fid}")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t("prev"), callback_data=f"fp:{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text=t("next"), callback_data=f"fp:{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="bm"))
    return builder.as_markup()


def history_kb(page: int, total_pages: int, lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t("prev"), callback_data=f"hp:{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text=t("next"), callback_data=f"hp:{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="🗑 Clear", callback_data="hc"))
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="bm"))
    return builder.as_markup()


def random_count_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for count in [10, 20, 50, 100]:
        builder.button(text=str(count), callback_data=f"r:{count}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=get_text("back", lang), callback_data="bm"))
    return builder.as_markup()


def language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbek", callback_data="l:uz")
    builder.button(text="🇺🇸 English", callback_data="l:en")
    builder.button(text="🇷🇺 Русский", callback_data="l:ru")
    builder.adjust(1)
    return builder.as_markup()


def leaderboard_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    builder.button(text=t("generators_leaderboard"), callback_data="lb:gen")
    builder.button(text=t("referrals_leaderboard"), callback_data="lb:ref")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="bm"))
    return builder.as_markup()


def profile_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    builder.button(text=t("daily_claim"), callback_data="db")
    builder.button(text="🎯 Referrals", callback_data="ref")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🏆 Leaderboard", callback_data="lb"))
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="bm"))
    return builder.as_markup()


def back_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("back", lang), callback_data="bm")
    return builder.as_markup()


def back_categories_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("back", lang), callback_data="bc")
    return builder.as_markup()


def admin_dashboard_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    builder.button(text=t("users"), callback_data="au")
    builder.button(text=t("broadcast"), callback_data="abr")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=t("add_channel"), callback_data="aac"))
    builder.row(InlineKeyboardButton(text=t("remove_channel"), callback_data="arc"))
    builder.row(InlineKeyboardButton(text=t("statistics"), callback_data="ast"))
    builder.row(InlineKeyboardButton(text=t("settings"), callback_data="aset"))
    builder.row(InlineKeyboardButton(text=t("ban_user"), callback_data="aban"))
    builder.row(InlineKeyboardButton(text=t("unban_user"), callback_data="aunb"))
    builder.row(InlineKeyboardButton(text=t("find_user"), callback_data="afind"))
    builder.row(InlineKeyboardButton(text=t("export_db"), callback_data="aexp"))
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="bm"))
    return builder.as_markup()


def force_join_kb(channels: List[Tuple[str, str]], lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    for title, link in channels:
        builder.button(text=f"📢 {title}", url=link)
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=t("check_subs"), callback_data="cs"))
    return builder.as_markup()


CATEGORY_DISPLAY = {
    "gaming": "🎮 Gaming Nicknames",
    "premium": "👑 Premium Nicknames",
    "cool": "🔥 Cool Nicknames",
    "invisible": "👻 Invisible Nicknames",
    "fancy_unicode": "⚡ Fancy Unicode Nicknames",
    "decorated": "🎨 Decorated Nicknames",
    "ai": "🤖 AI Nicknames",
    "ai_gen": "🤖 AI Nicknames",
    "hacker": "💀 Hacker Nicknames",
    "king": "👑 King Nicknames",
    "animal": "🐺 Animal Nicknames",
    "anime": "🌌 Anime Nicknames",
    "luxury": "💎 Luxury Nicknames",
    "couple": "❤️ Couple Nicknames",
    "cute": "🌸 Cute Nicknames",
    "dark": "🌙 Dark Nicknames",
    "space": "👽 Space Nicknames",
    "robot": "⚙ Robot Nicknames",
    "random": "🎲 Random Nicknames",
}
