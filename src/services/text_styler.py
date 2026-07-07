import random
from typing import List, Dict, Callable


FONT_STYLES: Dict[str, Callable[[str], str]] = {}


def _make_font(upper_start: int, lower_start: int, offset: int = 0) -> Callable[[str], str]:
    def transform(text: str) -> str:
        result = []
        for ch in text:
            if "A" <= ch <= "Z":
                result.append(chr(upper_start + (ord(ch) - 0x41) + offset))
            elif "a" <= ch <= "z":
                result.append(chr(lower_start + (ord(ch) - 0x61) + offset))
            else:
                result.append(ch)
        return "".join(result)
    return transform


def _register(name: str, fn: Callable[[str], str]):
    FONT_STYLES[name] = fn


_register("Mathematical Bold", _make_font(0x1D400, 0x1D41A))
_register("Mathematical Italic", _make_font(0x1D434, 0x1D44E))
_register("Mathematical Bold Italic", _make_font(0x1D468, 0x1D482))
_register("Script", _make_font(0x1D49C, 0x1D4B6))
_register("Bold Script", _make_font(0x1D4D0, 0x1D4EA))
_register("Fraktur", _make_font(0x1D504, 0x1D51E))
_register("Bold Fraktur", _make_font(0x1D56C, 0x1D586))
_register("Double-struck", _make_font(0x1D538, 0x1D552))
_register("Monospace", _make_font(0x1D670, 0x1D68A))
_register("Fullwidth", _make_font(0xFF21, 0xFF41))
_register("Circled", _make_font(0x24B6, 0x24D0))
_register("Parenthesized", _make_font(0x249C, 0x2488, offset=0x24B6 - 0x249C))  # fix offset
_register("Squared", _make_font(0x1F130, 0x1F150))


def _parenthesized(text: str) -> str:
    mapping = {
        "a": "⒜", "b": "⒝", "c": "⒞", "d": "⒟", "e": "⒠", "f": "⒡", "g": "⒢",
        "h": "⒣", "i": "⒤", "j": "⒥", "k": "⒦", "l": "⒧", "m": "⒨", "n": "⒩",
        "o": "⒪", "p": "⒫", "q": "⒬", "r": "⒭", "s": "⒮", "t": "⒯", "u": "⒰",
        "v": "⒱", "w": "⒲", "x": "⒳", "y": "⒴", "z": "⒵",
    }
    result = []
    for ch in text.lower():
        result.append(mapping.get(ch, ch))
    return "".join(result)


_register("Parenthesized", _parenthesized)


def _squared_neg(text: str) -> str:
    mapping = {
        "a": "🄰", "b": "🄱", "c": "🄲", "d": "🄳", "e": "🄴", "f": "🄵", "g": "🄶",
        "h": "🄷", "i": "🄸", "j": "🄹", "k": "🄺", "l": "🄻", "m": "🄼", "n": "🄽",
        "o": "🄾", "p": "🄿", "q": "🅀", "r": "🅁", "s": "🅂", "t": "🅃", "u": "🅄",
        "v": "🅅", "w": "🅆", "x": "🅇", "y": "🅈", "z": "🅉",
        "A": "🅰", "B": "🅱", "C": "🅲", "D": "🅳", "E": "🅴", "F": "🅵", "G": "🅶",
        "H": "🅷", "I": "🅸", "J": "🅹", "K": "🅺", "L": "🅻", "M": "🅼", "N": "🅽",
        "O": "🅾", "P": "🅿", "Q": "🆀", "R": "🆁", "S": "🆂", "T": "🆃", "U": "🆄",
        "V": "🆅", "W": "🆆", "X": "🆇", "Y": "🆈", "Z": "🆉",
    }
    result = []
    for ch in text:
        result.append(mapping.get(ch, ch))
    return "".join(result)


_register("Squared Negative", _squared_neg)


def _regional(text: str) -> str:
    mapping = {}
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        mapping[ch] = chr(0x1F1E6 + i)
    for i, ch in enumerate("abcdefghijklmnopqrstuvwxyz"):
        mapping[ch] = chr(0x1F1E6 + i)
    result = []
    for ch in text:
        mapped = mapping.get(ch, ch)
        result.append(mapped)
    return "\u200b".join(result)


_register("Regional Indicator", _regional)


def _superscript(text: str) -> str:
    sup = str.maketrans("0123456789+-=()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")
    sup_map = {
        "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ", "g": "ᵍ",
        "h": "ʰ", "i": "ⁱ", "j": "ʲ", "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ",
        "o": "ᵒ", "p": "ᵖ", "r": "ʳ", "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ",
        "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ",
    }
    result = []
    for ch in text.lower():
        result.append(sup_map.get(ch, ch.translate(sup)))
    return "".join(result)


_register("Superscript", _superscript)


def _subscript(text: str) -> str:
    sub_map = {
        "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅",
        "6": "₆", "7": "₇", "8": "₈", "9": "₉",
        "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
        "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "r": "ᵣ",
        "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ",
    }
    result = []
    for ch in text.lower():
        result.append(sub_map.get(ch, ch))
    return "".join(result)


_register("Subscript", _subscript)


def _small_caps(text: str) -> str:
    sc_map = {
        "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ",
        "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
        "o": "ᴏ", "p": "ᴘ", "q": "ꞯ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ",
        "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
    }
    result = []
    for ch in text.lower():
        result.append(sc_map.get(ch, ch))
    return "".join(result)


_register("Small Caps", _small_caps)


def _upside_down(text: str) -> str:
    mapping = {
        "a": "ɐ", "b": "q", "c": "ɔ", "d": "p", "e": "ǝ", "f": "ɟ", "g": "ɓ",
        "h": "ɥ", "i": "ᴉ", "j": "ɾ", "k": "ʞ", "l": "l", "m": "ɯ", "n": "u",
        "o": "o", "p": "d", "q": "b", "r": "ɹ", "s": "s", "t": "ʇ", "u": "n",
        "v": "ʌ", "w": "ʍ", "x": "x", "y": "ʎ", "z": "z",
        "A": "∀", "B": "𐐒", "C": "Ↄ", "D": "◖", "E": "Ǝ", "F": "Ⅎ", "G": "⅁",
        "H": "H", "I": "I", "J": "Ր", "K": "⋊", "L": "⅂", "M": "W", "N": "N",
        "O": "O", "P": "Ԁ", "Q": "Ό", "R": "ᴚ", "S": "S", "T": "⊥", "U": "∩",
        "V": "Λ", "W": "M", "X": "X", "Y": "⅄", "Z": "Z",
    }
    result = []
    for ch in text:
        result.append(mapping.get(ch, ch))
    return "".join(reversed(result))


_register("Upside Down", _upside_down)


FONT_NAMES = list(FONT_STYLES.keys())


DECORATIVE_TEMPLATES: List[Callable[[str], str]] = []


def _deco(prefix: str, suffix: str) -> Callable[[str], str]:
    return lambda t: f"{prefix}{t}{suffix}"


for p, s in [
    ("꧁", "꧂"), ("『", "』"), ("༒", "༒"), ("乂", "乂"), ("★", "★"),
    ("♛", "♛"), ("「", "」"), ("【", "】"), ("•", "•"), ("✦", "✦"),
    ("✧", "✧"), ("═", "═"), ("☠", "☠"), ("🔥", "🔥"), ("⚡", "⚡"),
    ("💀", "💀"), ("🎯", "🎯"), ("◥", "◤"), ("◤", "◢"), ("✿", "✿"),
    ("亗", "亗"), ("ꨄ", "ꨄ"), ("♡", "♡"), ("☆", "☆"), ("✧", "✧"),
    ("≛", "≛"), ("ᯓ", "ᯓ"), ("𖦹", "𖦹"), ("ᰔ", "ᰔ"), ("꒰", "꒱"),
    ("⎛", "⎞"), ("⎝", "⎠"), ("⫸", "⫷"), ("「", "」"), ("『", "』"),
    ("【", "】"), ("〖", "〗"), ("〘", "〙"), ("〚", "〛"), ("⋆", "⋆"),
    ("✶", "✶"), ("✴", "✴"), ("❋", "❋"), ("ꕤ", "ꕤ"), ("𑁍", "𑁍"),
    ("⁂", "⁂"), ("※", "※"), ("⁑", "⁑"), ("†", "†"), ("‡", "‡"),
    ("◈", "◈"), ("◇", "◇"), ("◉", "◉"), ("○", "○"), ("◎", "◎"),
    ("⬩", "⬩"), ("∙", "∙"), ("⋅", "⋅"), ("⋆", "⋆"),
]:
    DECORATIVE_TEMPLATES.append(_deco(p, s))


GAMING_TEMPLATES: List[Callable[[str], str]] = []


def _gaming(prefix: str, suffix: str) -> Callable[[str], str]:
    return lambda t: f"{prefix}{t.upper()}{suffix}"


for p, s in [
    ("", "メ"), ("乂", "乂"), ("", "ツ"), ("", "么"), ("", "亗"),
    ("", "★"), ("", "〆"), ("", "X"), ("", "✗"), ("", "✘"),
    ("", "☠"), ("", "♛"), ("✦", "✦"), ("⚡", "⚡"), ("🔥", "🔥"),
    ("", "〄"), ("", "ヅ"), ("", "ゾ"), ("", "シ"), ("", "ッ"),
    ("", "様"), ("", "殿"), ("", "鬼"), ("", "龍"), ("", "虎"),
    ("", "狼"), ("", "牙"), ("", "刃"), ("", "忍"), ("", "闇"),
    ("", "影"), ("", "風"), ("", "炎"), ("", "雷"), ("", "氷"),
    ("", "王"), ("", "将"), ("", "軍"), ("", "戦"), ("", "士"),
    ("✗", "✗"), ("✞", "✞"), ("卐", "卐"), ("卍", "卍"),
]:
    GAMING_TEMPLATES.append(_gaming(p, s))


SYMBOLS = [
    "⚡", "★", "☆", "☠", "♛", "✿", "꧁", "꧂", "亗", "乂",
    "メ", "ツ", "々", "〆", "彡", "ꨄ", "♡", "❤", "🔥", "💀",
    "🎯", "🏆", "👑", "⭐", "🌟", "✨", "💫", "⚔", "🛡", "🗡",
    "🏹", "🔮", "💎", "🌙", "☀", "⚜", "❄", "🌸", "🍀", "🎮",
    "🖥", "⌨", "🖱", "🎧", "📡", "🔭", "🔬", "⚗", "🧪", "⚙",
    "🔧", "🔨", "⚒", "🛠", "🔩", "⚙", "📐", "📏", "🔗", "💠",
    "🌀", "♾", "∞", "⚛", "☯", "✡", "☸", "☪", "☦", "♰",
    "♱", "✝", "☥", "🕉", "🔯", "🪯", "☮", "⚕", "☤", "🎵",
    "🎶", "♪", "♫", "♬", "🎼", "🎹", "🎸", "🎺", "🎻", "🪇",
]

EMOJI_STYLES = [
    ("🔥", "🔥"), ("👑", "👑"), ("⚡", "⚡"), ("☠", "☠"), ("🦅", "🦅"),
    ("💎", "💎"), ("🌟", "🌟"), ("✨", "✨"), ("🌙", "🌙"), ("☀", "☀"),
    ("🌸", "🌸"), ("🍀", "🍀"), ("🎯", "🎯"), ("🏆", "🏆"), ("⭐", "⭐"),
    ("❤️", "❤️"), ("💀", "💀"), ("🔮", "🔮"), ("⚔", "⚔"), ("🛡", "🛡"),
    ("🌀", "🌀"), ("♛", "♛"), ("🎮", "🎮"), ("🖥", "🖥"), ("📡", "📡"),
]


def _leet(ch: str) -> str:
    leet_map = {
        "a": "@", "A": "@",
        "b": "8", "B": "8",
        "e": "3", "E": "3",
        "g": "9", "G": "9",
        "i": "1", "I": "1",
        "l": "1", "L": "1",
        "o": "0", "O": "0",
        "s": "5", "S": "5",
        "t": "7", "T": "7",
        "z": "2", "Z": "2",
    }
    return leet_map.get(ch, ch)


class TextStyler:

    @staticmethod
    def apply_font(text: str, font_name: str) -> str | None:
        fn = FONT_STYLES.get(font_name)
        if fn:
            return fn(text)
        return None

    @staticmethod
    def get_all_font_styles(text: str) -> List[tuple[str, str]]:
        results = []
        seen = set()
        for name, fn in FONT_STYLES.items():
            try:
                transformed = fn(text)
                if transformed and transformed != text and transformed not in seen:
                    results.append((name, transformed))
                    seen.add(transformed)
            except Exception:
                continue
        return results

    @staticmethod
    def get_decorative_styles(text: str) -> List[str]:
        results = []
        seen = set()
        for tmpl in DECORATIVE_TEMPLATES:
            try:
                transformed = tmpl(text)
                if transformed and transformed not in seen:
                    results.append(transformed)
                    seen.add(transformed)
            except Exception:
                continue
        return results

    @staticmethod
    def get_gaming_styles(text: str) -> List[str]:
        results = []
        seen = set()
        for tmpl in GAMING_TEMPLATES:
            try:
                transformed = tmpl(text)
                if transformed and transformed not in seen:
                    results.append(transformed)
                    seen.add(transformed)
            except Exception:
                continue
        return results

    @staticmethod
    def get_symbol_variants(text: str, symbol: str) -> List[str]:
        return [
            f"{symbol}{text}",
            f"{text}{symbol}",
            f"{symbol}{text}{symbol}",
            f"{symbol} {text} {symbol}",
        ]

    @staticmethod
    def get_emoji_styles(text: str) -> List[str]:
        results = []
        seen = set()
        for left, right in EMOJI_STYLES:
            try:
                transformed = f"{left}{text}{right}"
                if transformed not in seen:
                    results.append(transformed)
                    seen.add(transformed)
            except Exception:
                continue
        return results

    @staticmethod
    def hacker_style(text: str) -> str:
        result = []
        for ch in text:
            if random.random() > 0.5:
                result.append(_leet(ch))
            else:
                result.append(ch)
        return "".join(result)

    @staticmethod
    def glitch_text(text: str, intensity: int = 2) -> str:
        zalgo_chars = [
            "\u0300", "\u0301", "\u0302", "\u0303", "\u0304", "\u0305",
            "\u0306", "\u0307", "\u0308", "\u0309", "\u030A", "\u030B",
            "\u030C", "\u030D", "\u030E", "\u030F", "\u0310", "\u0311",
            "\u0312", "\u0313", "\u0314", "\u0315", "\u0316", "\u0317",
            "\u0318", "\u0319", "\u031A", "\u031B", "\u031C", "\u031D",
            "\u031E", "\u031F", "\u0320", "\u0321", "\u0322", "\u0323",
            "\u0324", "\u0325", "\u0326", "\u0327", "\u0328", "\u0329",
            "\u032A", "\u032B", "\u032C", "\u032D", "\u032E", "\u032F",
            "\u0330", "\u0331", "\u0332", "\u0333", "\u0334", "\u0335",
            "\u0336", "\u0337", "\u0338", "\u0339", "\u033A", "\u033B",
            "\u033C", "\u033D", "\u033E", "\u033F",
        ]
        result = []
        for ch in text:
            result.append(ch)
            for _ in range(random.randint(0, intensity)):
                result.append(random.choice(zalgo_chars))
        return "".join(result)

    @staticmethod
    def invisible(text: str) -> str:
        invisible_chars = [
            "\u2060", "\u2061", "\u2062", "\u2063", "\u2064",
            "\u2066", "\u2067", "\u2068", "\u2069", "\u200B",
            "\u200C", "\u200D", "\uFEFF",
        ]
        return "".join(random.choices(invisible_chars, k=len(text) * 2))

    @staticmethod
    def pubg_style(text: str) -> str:
        styles = [
            lambda t: f"「{t.upper()}」",
            lambda t: f"⚔{t.upper()}⚔",
            lambda t: f"🎯{t.upper()}🎯",
            lambda t: f"『{t}』",
            lambda t: f"《{t.upper()}》",
            lambda t: f"〔{t.upper()}〕",
            lambda t: f"〖{t.upper()}〗",
            lambda t: f"「{t}」🔥",
            lambda t: f"🔥「{t}」",
            lambda t: f"✦{t.upper()}✦",
            lambda t: f"{t.upper()}〄",
            lambda t: f"☠{t.upper()}☠",
            lambda t: f"★{t.upper()}★",
            lambda t: f"『{t}』⚡",
            lambda t: f"🏆{t.upper()}🏆",
            lambda t: f"👑{t.upper()}👑",
            lambda t: f"💀{t.upper()}💀",
            lambda t: f"⚡{t.upper()}⚡",
            lambda t: f"🔥{t.upper()}🔥",
            lambda t: f"⭐{t.upper()}⭐",
        ]
        return [s(text) for s in styles]

    @staticmethod
    def vip_style(text: str) -> List[str]:
        styles = [
            lambda t: f"💎 Vɪᴘ • {t} • Vɪᴘ 💎",
            lambda t: f"👑 Pʀᴇᴍɪᴜᴍ 👑 {t}",
            lambda t: f"⭐ {t} ⭐",
            lambda t: f"✦ Pʀᴇᴍɪᴜᴍ ✦ {t}",
            lambda t: f"『V』『I』『P』 {t}",
            lambda t: f"💎Eʟɪᴛᴇ💎{t}",
            lambda t: f"★彡 {t} 彡★",
            lambda t: f"「V」「I」「P」 {t}",
            lambda t: f"✧ {t} ✧",
            lambda t: f"❖ {t} ❖",
            lambda t: f"🏆 {t} 🏆",
            lambda t: f"𝕰𝖑𝖎𝖙𝖊 {t}",
            lambda t: f"༺{t}༻",
            lambda t: f"×͜× {t} ×͜×",
            lambda t: f"꧁༺{t}༻꧂",
        ]
        return [s(text) for s in styles]

    @staticmethod
    def cute_style(text: str) -> List[str]:
        styles = [
            lambda t: f"🌸 {t} 🌸",
            lambda t: f"✨ {t} ✨",
            lambda t: f"♡ {t} ♡",
            lambda t: f"ꨄ {t} ꨄ",
            lambda t: f"✿ {t} ✿",
            lambda t: f"「{t}」♡",
            lambda t: f"♥ {t} ♥",
            lambda t: f"☆ {t} ☆",
            lambda t: f"✧ {t} ✧",
            lambda t: f"⋆｡°✩ {t} ✩°｡⋆",
            lambda t: f"♡́ {t} ̀♡",
            lambda t: f"✽ {t} ✽",
            lambda t: f"❤️{t}❤️",
            lambda t: f"💕(｡◕‿◕｡)💕",
        ]
        return [s(text) for s in styles]

    @staticmethod
    def dark_style(text: str) -> List[str]:
        styles = [
            lambda t: f"☠ {t} ☠",
            lambda t: f"🖤 {t} 🖤",
            lambda t: f"💀 {t} 💀",
            lambda t: f"🌙 {t} 🌙",
            lambda t: f"☾ {t} ☽",
            lambda t: f"꧁☠{t}☠꧂",
            lambda t: f"乂{t}乂",
            lambda t: f"♱ {t} ♱",
            lambda t: f"† {t} †",
            lambda t: f"‡ {t} ‡",
            lambda t: f"✟ {t} ✟",
            lambda t: f"⚔{t}⚔",
            lambda t: f"🗡{t}🗡",
            lambda t: f"♠ {t} ♠",
            lambda t: f"⛓ {t} ⛓",
            lambda t: f"🕷 {t} 🕷",
        ]
        return [s(text) for s in styles]
