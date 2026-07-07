import random
import string
from typing import List, Optional


def generate_referral_code(length: int = 10) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def chunk_list(items: list, size: int) -> list:
    return [items[i:i + size] for i in range(0, len(items), size)]


def format_number(num: int) -> str:
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


def escape_markdown(text: str) -> str:
    special_chars = r"_*[]()~`>#+-=|{}.!"
    return ''.join(f"\\{c}" if c in special_chars else c for c in text)


def truncate_text(text: str, max_length: int = 100) -> str:
    return text[:max_length] + "..." if len(text) > max_length else text


async def safe_execute(coro):
    try:
        return await coro
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Safe execute error: {e}", exc_info=True)
        return None
