from typing import Callable, Awaitable, Any, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config
from src.domain.enums import Language
from src.utils.localizer import get_text
from src.infrastructure.repository import UserRepository


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
            session: AsyncSession | None = data.get("session")
            if session and user_id:
                try:
                    repo = UserRepository(session)
                    user = await repo.get(user_id)
                    if user:
                        lang = user.language
                except Exception:
                    pass

            text = get_text("maintenance", lang)
            if isinstance(event, Message):
                await event.answer(text)
            elif isinstance(event, CallbackQuery) and event.message:
                await event.message.answer(text)
                await event.answer()
            return

        return await handler(event, data)
