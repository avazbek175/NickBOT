from aiogram.filters import Filter
from aiogram.types import Message
from src.config import config


class ForceJoinCheck(Filter):
    async def __call__(self, message: Message) -> bool:
        return True
