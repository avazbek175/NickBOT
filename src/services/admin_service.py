from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import User, AdminLog, ForceChannel
from src.domain.enums import UserStatus
from src.infrastructure.repository import UserRepository, ForceChannelRepository, BroadcastRepository, SettingRepository
from src.config import config


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.channel_repo = ForceChannelRepository(session)
        self.broadcast_repo = BroadcastRepository(session)
        self.settings_repo = SettingRepository(session)

    def is_admin(self, user_id: int) -> bool:
        return user_id in config.admin_id_list

    async def get_dashboard(self) -> dict:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        total_users = await self.user_repo.count()
        today_users = await self.user_repo.count(User.created_at >= today_start)
        yesterday_users = await self.user_repo.count(
            and_(User.created_at >= yesterday_start, User.created_at < today_start)
        )
        weekly_users = await self.user_repo.count(User.created_at >= week_start)
        monthly_users = await self.user_repo.count(User.created_at >= month_start)
        premium_users = await self.user_repo.count(User.is_premium == True)

        result = await self.session.execute(
            select(func.coalesce(func.sum(User.total_generated), 0))
        )
        total_gen = result.scalar()

        today_gen_result = await self.session.execute(
            select(func.coalesce(func.sum(User.total_generated), 0)).where(User.updated_at >= today_start)
        )
        today_gen = today_gen_result.scalar()

        broadcasts = await self.broadcast_repo.count()

        from src.infrastructure.cache import redis
        redis_ok = False
        try:
            if redis:
                await redis.ping()
                redis_ok = True
        except Exception:
            redis_ok = False

        return {
            "users": total_users,
            "today": today_users,
            "yesterday": yesterday_users,
            "weekly": weekly_users,
            "monthly": monthly_users,
            "premium": premium_users,
            "gen_today": today_gen,
            "gen_total": total_gen,
            "broadcasts": broadcasts,
            "server_ok": True,
            "db_ok": True,
            "redis_ok": redis_ok,
            "uptime": "Online",
        }

    async def get_settings(self) -> dict:
        return await self.settings_repo.get_all()

    async def update_setting(self, key: str, value: str):
        await self.settings_repo.set(key, value)

    async def log_action(self, admin_id: int, action: str, details: str = None):
        log = AdminLog(admin_id=admin_id, action=action, details=details)
        self.session.add(log)
        await self.session.commit()

    async def ban_user(self, user_id: int) -> bool:
        user = await self.user_repo.get(user_id)
        if user:
            await self.user_repo.update(user_id, status=UserStatus.BANNED)
            return True
        return False

    async def unban_user(self, user_id: int) -> bool:
        user = await self.user_repo.get(user_id)
        if user:
            await self.user_repo.update(user_id, status=UserStatus.ACTIVE)
            return True
        return False
