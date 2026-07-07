from aiogram.filters import Filter
from aiogram.types import Message
from src.config import config


class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in config.admin_id_list
