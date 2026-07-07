import random
from typing import List, Optional


GAMING_NAMES = [
    "ShadowX", "GhostOP", "NightHunter", "Reaper", "Venom",
    "Phantom", "Cipher", "Viper", "Frost", "Blaze",
    "Storm", "Nemesis", "Apex", "Titan", "Creed",
    "Havoc", "Wraith", "Rogue", "Sniper", "Fury",
    "Eclipse", "Cyber", "Neon", "Omega", "Delta",
    "Savage", "Predator", "Silent", "Ghost", "Flash",
    "Shadow", "Killer", "Night", "Hunter", "Pro",
    "Elite", "Master", "Legend", "Warrior", "Slayer",
]

PREMIUM_NAMES = [
    "Aether", "Noctis", "Velorian", "Kaizen", "Virex",
    "Orion", "Zephyr", "Luxor", "Nyx", "Solus",
    "Aurelius", "Draven", "Kael", "Magnus", "Onyx",
    "Riven", "Thorne", "Valor", "Zarek", "Kross",
    "Veyron", "Xylon", "Crest", "Drift", "Fable",
]

COOL_NAMES = [
    "Nexo", "Kyro", "Raze", "Nova", "Ryzen",
    "Zero", "Blitz", "Cruz", "Daze", "Edge",
    "Flex", "Grit", "Hype", "Jolt", "Kix",
    "Lynx", "Maxx", "Nix", "Onyx", "Pulse",
    "Ryze", "Skim", "Trek", "Vex", "Zest",
]

HACKER_NAMES = [
    "Byte", "Null", "Kernel", "Cipher", "Zero",
    "Hex", "Root", "Shell", "Hack", "Code",
    "Bit", "Logic", "Glitch", "Crash", "Proxy",
    "Flux", "Void", "Bash", "Crypt", "DDoS",
    "Exploit", "Firewall", "Malware", "Phish", "Sploit",
]

KING_NAMES = [
    "King", "Royal", "Lord", "Supreme", "Emperor",
    "Prince", "Duke", "Baron", "Count", "Sultan",
    "Caesar", "Kaiser", "Pharaoh", "Rajah", "Tsar",
    "Monarch", "Crown", "Regal", "Majesty", "Noble",
]

ANIMAL_NAMES = [
    "Wolf", "Tiger", "Falcon", "Dragon", "Fox",
    "Panther", "Eagle", "Lion", "Bear", "Hawk",
    "Viper", "Cobra", "Shark", "Raven", "Lynx",
    "Phoenix", "Jaguar", "Cheetah", "Vulture", "Coyote",
]

ANIME_NAMES = [
    "Akuma", "Yoru", "Raijin", "Kitsune", "Akira",
    "Sakura", "Kenji", "Ryuko", "Hikaru", "Sora",
    "Naruto", "Sasuke", "Ichigo", "Rukia", "Goku",
    "Vegeta", "Luffy", "Zoro", "Mikasa", "Levi",
    "Eren", "Tanjiro", "Nezuko", "Gojo", "Itachi",
]

LUXURY_NAMES = [
    "Monarch", "Imperium", "Diamond", "Platinum", "Royal",
    "Crystal", "Onyx", "Jade", "Ruby", "Sapphire",
    "Gold", "Silver", "Bronze", "Titanium", "Velvet",
    "Silk", "Crown", "Noble", "Elite", "Prestige",
]

CUTE_NAMES = [
    "Cutie", "Sweetie", "Honey", "Bunny", "Kitty",
    "Panda", "Cookie", "Candy", "Pudding", "Mochi",
    "Peach", "Cherry", "Berry", "Sunny", "Luna",
    "Starry", "Daisy", "Lily", "Rose", "Ivy",
]

DARK_NAMES = [
    "Shadow", "Darkness", "Night", "Oblivion", "Void",
    "Abyss", "Chaos", "Doom", "Gloom", "Midnight",
    "Umbra", "Tenebris", "Nox", "Obsidian", "Raven",
    "Shade", "Dusk", "Twilight", "Dark", "Black",
]

SPACE_NAMES = [
    "Nebula", "Cosmos", "Orion", "Sirius", "Vega",
    "Andromeda", "Asteroid", "Comet", "Eclipse", "Galaxy",
    "Jupiter", "Mars", "Neptune", "Nova", "Pluto",
    "Saturn", "Solar", "Stellar", "Uranus", "Venus",
]

ROBOT_NAMES = [
    "Cyborg", "Android", "Bot", "Mech", "Robo",
    "Droid", "Unit", "Chip", "Core", "Pixel",
    "Matrix", "Circuit", "Binary", "Cache", "Logic",
    "Servo", "Steel", "Synth", "Tech", "Volt",
]

COUPLE_NAMES = [
    ("Love", "Heart"), ("Romeo", "Juliet"), ("Adam", "Eve"),
    ("Bonnie", "Clyde"), ("Sun", "Moon"), ("Salt", "Pepper"),
    ("King", "Queen"), ("Prince", "Princess"), ("Star", "Sky"),
    ("Fire", "Ice"), ("Day", "Night"), ("Light", "Dark"),
    ("Ocean", "Wave"), ("Rain", "Cloud"), ("Sugar", "Spice"),
    ("Candy", "Cane"), ("Lucky", "Charm"), ("Peach", "Mango"),
    ("Honey", "Bee"), ("Ace", "Spade"),
]

INVISIBLE_CHARS = [
    "\u2060",  # WORD JOINER
    "\u2061",  # FUNCTION APPLICATION
    "\u2062",  # INVISIBLE TIMES
    "\u2063",  # INVISIBLE SEPARATOR
    "\u2064",  # INVISIBLE PLUS
    "\u2066",  # LEFT-TO-RIGHT ISOLATE
    "\u2067",  # RIGHT-TO-LEFT ISOLATE
    "\u2068",  # FIRST STRONG ISOLATE
    "\u2069",  # POP DIRECTIONAL ISOLATE
    "\u200B",  # ZERO WIDTH SPACE
    "\u200C",  # ZERO WIDTH NON-JOINER
    "\u200D",  # ZERO WIDTH JOINER
    "\uFEFF",  # ZERO WIDTH NO-BREAK SPACE
]

DECORATIONS = [
    ("꧁", "꧂", "Avaz"),
    ("『", "』", "Avaz"),
    ("༒", "༒", "Avaz"),
    ("乂", "乂", "Avaz"),
    ("★", "★", "Avaz"),
    ("♛", "♛", "Avaz"),
    ("「", "」", "Avaz"),
    ("【", "】", "Avaz"),
    ("『", "』", "Avaz"),
    ("•", "•", "Avaz"),
    ("✦", "✦", "Avaz"),
    ("✧", "✧", "Avaz"),
    ("═", "═", "Avaz"),
    ("☠", "☠", "Avaz"),
    ("🔥", "🔥", "Avaz"),
    ("⚡", "⚡", "Avaz"),
    ("💀", "💀", "Avaz"),
    ("🎯", "🎯", "Avaz"),
]


class NicknameService:

    CATEGORY_MAP = {
        "gaming": ("🎮 Gaming", GAMING_NAMES),
        "premium": ("👑 Premium", PREMIUM_NAMES),
        "cool": ("🔥 Cool", COOL_NAMES),
        "hacker": ("💀 Hacker", HACKER_NAMES),
        "king": ("👑 King", KING_NAMES),
        "animal": ("🐺 Animal", ANIMAL_NAMES),
        "anime": ("🌌 Anime", ANIME_NAMES),
        "luxury": ("💎 Luxury", LUXURY_NAMES),
        "cute": ("🌸 Cute", CUTE_NAMES),
        "dark": ("🌙 Dark", DARK_NAMES),
        "space": ("👽 Space", SPACE_NAMES),
        "robot": ("⚙ Robot", ROBOT_NAMES),
    }

    @staticmethod
    def generate_name(category: str) -> str:
        if category == "invisible":
            return NicknameService.generate_invisible()
        if category == "fancy_unicode":
            return NicknameService.generate_fancy_unicode()
        if category == "decorated":
            return NicknameService.generate_decorated()
        if category == "couple":
            pair = random.choice(COUPLE_NAMES)
            return f"{pair[0]} & {pair[1]}"
        if category == "ai":
            return NicknameService.generate_ai_name()
        if category == "random":
            cat = random.choice(list(NicknameService.CATEGORY_MAP.keys()))
            return NicknameService.generate_name(cat)

        entry = NicknameService.CATEGORY_MAP.get(category)
        if not entry:
            entry = ("🎲 Random", GAMING_NAMES + PREMIUM_NAMES + COOL_NAMES)
        names = entry[1]
        name = random.choice(names)
        suffix = random.choice(["", "X", "OP", "Pro", "YT", "007", "21", "42", "99", "VR", random.choice("123456789")])
        if suffix and random.random() > 0.3:
            name = f"{name}{suffix}"
        return name

    @staticmethod
    def generate_multiple(category: str, count: int) -> List[str]:
        names = set()
        attempts = 0
        while len(names) < count and attempts < count * 10:
            names.add(NicknameService.generate_name(category))
            attempts += 1
        return list(names)[:count]

    @staticmethod
    def generate_invisible() -> str:
        length = random.randint(4, 12)
        return "".join(random.choices(INVISIBLE_CHARS, k=length))

    @staticmethod
    def generate_fancy_unicode() -> str:
        base = random.choice(GAMING_NAMES + PREMIUM_NAMES + COOL_NAMES)
        styles = [
            lambda s: "".join(chr(0x1D4D0 + ord(c) - 0x41) if "A" <= c <= "Z" else
                             chr(0x1D4EA + ord(c) - 0x61) if "a" <= c <= "z" else c for c in s),
            lambda s: "".join(chr(0x1D504 + ord(c) - 0x41) if "A" <= c <= "Z" else
                             chr(0x1D51E + ord(c) - 0x61) if "a" <= c <= "z" else c for c in s),
            lambda s: "".join(chr(0x1D400 + ord(c) - 0x41) if "A" <= c <= "Z" else
                             chr(0x1D41A + ord(c) - 0x61) if "a" <= c <= "z" else c for c in s),
            lambda s: "".join(chr(0xFF21 + ord(c) - 0x41) if "A" <= c <= "Z" else
                             chr(0xFF41 + ord(c) - 0x61) if "a" <= c <= "z" else c for c in s),
            lambda s: "".join(chr(0x1D56C + ord(c) - 0x41) if "A" <= c <= "Z" else
                             chr(0x1D586 + ord(c) - 0x61) if "a" <= c <= "z" else c for c in s),
        ]
        style = random.choice(styles)
        return style(base)

    @staticmethod
    def generate_decorated() -> str:
        base = random.choice(GAMING_NAMES + PREMIUM_NAMES + COOL_NAMES)
        deco = random.choice(DECORATIONS)
        return f"{deco[0]}{base}{deco[1]}"

    @staticmethod
    def generate_ai_name() -> str:
        prefixes = [
            "Zero", "Cyber", "Neo", "Dark", "Ice", "Fire", "Shadow", "Ghost",
            "Null", "Hex", "Byte", "Kernel", "Root", "Alpha", "Omega", "Proto",
            "Quantum", "Crypto", "Vortex", "Phantom", "Nova", "Eclipse",
        ]
        suffixes = [
            "Trace", "Ghost", "Void", "Byte", "Core", "X", "Hawk", "Wolf",
            "Strike", "Blaze", "Storm", "Fury", "Cipher", "Proxy", "Shell",
            "Pulse", "Drift", "Crash", "Flux", "Shade",
        ]
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        return f"{prefix}{suffix}"

    @staticmethod
    def search(query: str, limit: int = 10) -> List[str]:
        query_lower = query.lower()
        results = []
        all_names = (
            GAMING_NAMES + PREMIUM_NAMES + COOL_NAMES + HACKER_NAMES
            + KING_NAMES + ANIMAL_NAMES + ANIME_NAMES + LUXURY_NAMES
            + CUTE_NAMES + DARK_NAMES + SPACE_NAMES + ROBOT_NAMES
        )
        seen = set()
        for name in all_names:
            if query_lower in name.lower() and name not in seen:
                results.append(name)
                seen.add(name)
        return results[:limit]
