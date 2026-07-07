import asyncio
import logging
from typing import Optional
from datetime import datetime
from aiogram import Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import Broadcast
from src.domain.enums import BroadcastStatus, BroadcastType
from src.infrastructure.repository import BroadcastRepository, UserRepository

logger = logging.getLogger(__name__)


class BroadcastService:
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot
        self.repo = BroadcastRepository(session)
        self.user_repo = UserRepository(session)

    async def start_broadcast(self, broadcast_id: int, message: Message):
        broadcast = await self.session.get(Broadcast, broadcast_id)
        if not broadcast:
            return

        broadcast.status = BroadcastStatus.ACTIVE
        await self.session.commit()

        user_ids = await self.user_repo.all_ids()
        broadcast.total_count = len(user_ids)
        await self.session.commit()

        success = 0
        fail = 0
        batch_size = 30

        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i:i + batch_size]
            tasks = []
            for uid in batch:
                tasks.append(self._send_message(uid, broadcast, message))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if r is True:
                    success += 1
                else:
                    fail += 1
            await asyncio.sleep(0.5)

        broadcast.success_count = success
        broadcast.fail_count = fail
        broadcast.status = BroadcastStatus.COMPLETED
        broadcast.completed_at = datetime.utcnow()
        await self.session.commit()

    async def _send_message(self, user_id: int, broadcast: Broadcast, original_message: Message) -> bool:
        try:
            if broadcast.broadcast_type == BroadcastType.TEXT:
                await self.bot.send_message(user_id, broadcast.content)
            elif broadcast.broadcast_type == BroadcastType.PHOTO:
                await self.bot.send_photo(user_id, broadcast.file_id, caption=broadcast.caption)
            elif broadcast.broadcast_type == BroadcastType.VIDEO:
                await self.bot.send_video(user_id, broadcast.file_id, caption=broadcast.caption)
            elif broadcast.broadcast_type == BroadcastType.ANIMATION:
                await self.bot.send_animation(user_id, broadcast.file_id, caption=broadcast.caption)
            elif broadcast.broadcast_type == BroadcastType.DOCUMENT:
                await self.bot.send_document(user_id, broadcast.file_id, caption=broadcast.caption)
            elif broadcast.broadcast_type == BroadcastType.VOICE:
                await self.bot.send_voice(user_id, broadcast.file_id, caption=broadcast.caption)
            elif broadcast.broadcast_type == BroadcastType.AUDIO:
                await self.bot.send_audio(user_id, broadcast.file_id, caption=broadcast.caption)
            elif broadcast.broadcast_type == BroadcastType.STICKER:
                await self.bot.send_sticker(user_id, broadcast.file_id)
            return True
        except Exception as e:
            logger.warning(f"Broadcast failed to {user_id}: {e}")
            return False
