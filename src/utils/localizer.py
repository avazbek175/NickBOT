import json
import os
from typing import Optional
from src.domain.enums import Language


class Localizer:
    _cache: dict = {}

    @classmethod
    def load_locale(cls, lang: Language) -> dict:
        lang_code = lang.value
        if lang_code in cls._cache:
            return cls._cache[lang_code]
        path = os.path.join("locales", f"{lang_code}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cls._cache[lang_code] = data
            return data
        except FileNotFoundError:
            if lang_code != "en":
                return cls.load_locale(Language.ENGLISH)
            return {}

    @classmethod
    def get(cls, key: str, lang: Language = Language.ENGLISH, **kwargs) -> str:
        locale = cls.load_locale(lang)
        text = locale.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text


def get_text(key: str, lang: Language = Language.ENGLISH, **kwargs) -> str:
    return Localizer.get(key, lang, **kwargs)
