from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.utils.localizer import get_text
from src.domain.enums import Language


def main_menu_kb(lang: Language = Language.UZBEK) -> ReplyKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"{t('generate')}")],
            [KeyboardButton(text=f"{t('categories')}"), KeyboardButton(text=f"{t('random')}")],
            [KeyboardButton(text=f"{t('favorites')}"), KeyboardButton(text=f"{t('history')}")],
            [KeyboardButton(text=f"{t('search')}"), KeyboardButton(text=f"{t('profile')}")],
            [KeyboardButton(text=f"{t('language')}"), KeyboardButton(text=f"{t('help')}")],
        ],
        resize_keyboard=True,
        input_field_placeholder="NickForge AI",
    )
    return kb


def admin_main_kb(lang: Language = Language.UZBEK) -> ReplyKeyboardMarkup:
    t = lambda k: get_text(k, lang)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("admin_dashboard"))],
            [KeyboardButton(text=t("users")), KeyboardButton(text=t("broadcast"))],
            [KeyboardButton(text=t("add_channel")), KeyboardButton(text=t("remove_channel"))],
            [KeyboardButton(text=t("statistics")), KeyboardButton(text=t("settings"))],
            [KeyboardButton(text=t("daily_bonus")), KeyboardButton(text=t("referral_settings"))],
            [KeyboardButton(text=t("ban_user")), KeyboardButton(text=t("unban_user"))],
            [KeyboardButton(text=t("find_user")), KeyboardButton(text=t("export_db"))],
            [KeyboardButton(text=t("logs")), KeyboardButton(text=t("home"))],
        ],
        resize_keyboard=True,
    )
    return kb
