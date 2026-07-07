from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional
from src.utils.localizer import get_text
from src.domain.enums import Language


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
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="back_menu"))
    return builder.as_markup()


def nickname_action_kb(nickname: str, category: str, is_favorite: bool = False, lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    builder.button(text=t("copy"), callback_data=f"copy:{nickname}")
    if is_favorite:
        builder.button(text="✅ " + t("save"), callback_data=f"fav_del:{nickname}")
    else:
        builder.button(text=t("save"), callback_data=f"fav_add:{nickname}:{category}")
    builder.button(text=t("next"), callback_data=f"gen_more:{category}")
    builder.adjust(2, 1)
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="back_categories"))
    builder.row(InlineKeyboardButton(text=t("home"), callback_data="back_menu"))
    return builder.as_markup()


def nickname_list_action_kb(category: str, lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    builder.button(text=t("next"), callback_data=f"gen_more:{category}")
    builder.button(text=t("back"), callback_data="back_categories")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=t("home"), callback_data="back_menu"))
    return builder.as_markup()


def favorites_kb(favs: List[tuple], page: int, total_pages: int, lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    for fid, nickname in favs:
        builder.button(text=f"🗑 {nickname[:20]}", callback_data=f"fav_del_id:{fid}")
    builder.adjust(1)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t("prev"), callback_data=f"fav_page:{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text=t("next"), callback_data=f"fav_page:{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="back_menu"))
    return builder.as_markup()


def history_kb(page: int, total_pages: int, lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t("prev"), callback_data=f"hist_page:{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text=t("next"), callback_data=f"hist_page:{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="🗑 Clear", callback_data="hist_clear"))
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="back_menu"))
    return builder.as_markup()


def random_count_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for count in [10, 20, 50, 100]:
        builder.button(text=str(count), callback_data=f"rand:{count}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=get_text("back", lang), callback_data="back_menu"))
    return builder.as_markup()


def language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbek", callback_data="lang:uz")
    builder.button(text="🇺🇸 English", callback_data="lang:en")
    builder.button(text="🇷🇺 Русский", callback_data="lang:ru")
    builder.adjust(1)
    return builder.as_markup()


def leaderboard_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    builder.button(text=t("generators_leaderboard"), callback_data="lb:gen")
    builder.button(text=t("referrals_leaderboard"), callback_data="lb:ref")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="back_menu"))
    return builder.as_markup()


def profile_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    builder.button(text=t("daily_claim"), callback_data="daily_bonus")
    builder.button(text=t("referral_text").split("\n")[0][:20], callback_data="referral")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=t("leaderboard_title").split()[0] + " 🏆", callback_data="leaderboard"))
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="back_menu"))
    return builder.as_markup()


def back_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("back", lang), callback_data="back_menu")
    return builder.as_markup()


def back_categories_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("back", lang), callback_data="back_categories")
    return builder.as_markup()


# Admin keyboards
def admin_dashboard_kb(lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    builder.button(text=t("users"), callback_data="admin:users")
    builder.button(text=t("broadcast"), callback_data="admin:broadcast")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=t("add_channel"), callback_data="admin:add_channel"))
    builder.row(InlineKeyboardButton(text=t("remove_channel"), callback_data="admin:remove_channel"))
    builder.row(InlineKeyboardButton(text=t("statistics"), callback_data="admin:stats"))
    builder.row(InlineKeyboardButton(text=t("settings"), callback_data="admin:settings"))
    builder.row(InlineKeyboardButton(text=t("daily_bonus"), callback_data="admin:bonus"))
    builder.row(InlineKeyboardButton(text=t("ban_user"), callback_data="admin:ban"))
    builder.row(InlineKeyboardButton(text=t("unban_user"), callback_data="admin:unban"))
    builder.row(InlineKeyboardButton(text=t("find_user"), callback_data="admin:find"))
    builder.row(InlineKeyboardButton(text=t("export_db"), callback_data="admin:export"))
    builder.row(InlineKeyboardButton(text=t("back"), callback_data="back_menu"))
    return builder.as_markup()


def force_join_kb(channels: List[tuple], lang: Language = Language.UZBEK) -> InlineKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    builder = InlineKeyboardBuilder()
    for title, link in channels:
        builder.button(text=f"📢 {title}", url=link)
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text=t("check_subs"), callback_data="check_subs"))
    return builder.as_markup()
