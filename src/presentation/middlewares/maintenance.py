from typing import Callable, Awaitable, Any, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from src.config import config
from src.domain.enums import Language
from src.utils.localizer import get_text


class MaintenanceMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        if config.maintenance_mode:
            user_id = None
            if isinstance(event, Message):
                user_id = event.from_user.id
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id

            if user_id and user_id in config.admin_id_list:
                return await handler(event, data)

            lang = Language.UZBEK
            if isinstance(event, Message) and event.from_user:
                lang = Language.UZBEK
            elif isinstance(event, CallbackQuery) and event.from_user:
                lang = Language.UZBEK

            text = get_text("maintenance", lang)
            if isinstance(event, Message):
                await event.answer(text)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(text)
                await event.answer()
            return

        return await handler(event, data)
