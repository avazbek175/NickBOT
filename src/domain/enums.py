from enum import Enum


class Language(str, Enum):
    UZBEK = "uz"
    ENGLISH = "en"
    RUSSIAN = "ru"


class NicknameCategory(str, Enum):
    GAMING = "gaming"
    PREMIUM = "premium"
    COOL = "cool"
    INVISIBLE = "invisible"
    FANCY_UNICODE = "fancy_unicode"
    DECORATED = "decorated"
    AI = "ai"
    HACKER = "hacker"
    KING = "king"
    ANIMAL = "animal"
    ANIME = "anime"
    LUXURY = "luxury"
    COUPLE = "couple"
    CUTE = "cute"
    DARK = "dark"
    SPACE = "space"
    ROBOT = "robot"
    RANDOM = "random"


class UserStatus(str, Enum):
    ACTIVE = "active"
    BANNED = "banned"
    PREMIUM = "premium"


class BroadcastType(str, Enum):
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    ANIMATION = "animation"
    DOCUMENT = "document"
    VOICE = "voice"
    AUDIO = "audio"
    STICKER = "sticker"


class BroadcastStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
