import time
from typing import Callable, Awaitable, Dict, Tuple, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from src.config import config


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.user_times: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            if user_id in config.admin_id_list:
                return await handler(event, data)

            now = time.time()
            last_time = self.user_times.get(user_id, 0)
            if now - last_time < self.rate_limit:
                return
            self.user_times[user_id] = now

        return await handler(event, data)
