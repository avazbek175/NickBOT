from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import User, ReferralLog, BonusLog
from src.domain.enums import Language, UserStatus
from src.infrastructure.repository import UserRepository
from src.config import config


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def get_or_create(self, user_id: int, username: str = None,
                            first_name: str = None, last_name: str = None,
                            referred_by: int = None) -> User:
        user = await self.repo.get(user_id)
        if not user:
            user = await self.repo.create(user_id, username, first_name, last_name, referred_by)
            if referred_by and config.referral_enabled:
                await self._process_referral(referred_by, user_id)
        else:
            update_data = {}
            if username and user.username != username:
                update_data["username"] = username
            if first_name and user.first_name != first_name:
                update_data["first_name"] = first_name
            if last_name and user.last_name != last_name:
                update_data["last_name"] = last_name
            if update_data:
                await self.repo.update(user_id, **update_data)
        return user

    async def _process_referral(self, referrer_id: int, new_user_id: int):
        referrer = await self.repo.get(referrer_id)
        if not referrer or referrer_id == new_user_id:
            return
        if referrer.status == UserStatus.BANNED:
            return
        coins = config.referral_coins
        referrer.coins += coins
        referrer.referral_count += 1
        log = ReferralLog(referrer_id=referrer_id, referred_id=new_user_id, coins_awarded=coins)
        self.session.add(log)
        await self.session.commit()

    async def increment_generated(self, user_id: int):
        user = await self.repo.get(user_id)
        if user:
            user.total_generated += 1
            await self.session.commit()

    async def daily_bonus_available(self, user_id: int) -> Tuple[bool, Optional[int]]:
        user = await self.repo.get(user_id)
        if not user:
            return False, None
        if not user.last_daily_bonus:
            return True, config.daily_bonus_coins
        now = datetime.utcnow()
        last = user.last_daily_bonus.replace(tzinfo=None)
        if now.date() > last.date():
            return True, config.daily_bonus_coins
        next_available = last + timedelta(days=1)
        remaining = int((next_available - now).total_seconds())
        return False, remaining

    async def claim_daily_bonus(self, user_id: int) -> int:
        user = await self.repo.get(user_id)
        if not user:
            return 0
        user.coins += config.daily_bonus_coins
        user.last_daily_bonus = datetime.utcnow()
        log = BonusLog(user_id=user_id, amount=config.daily_bonus_coins, bonus_type="daily")
        self.session.add(log)
        await self.session.commit()
        return config.daily_bonus_coins

    async def get_profile_data(self, user_id: int) -> dict:
        user = await self.repo.get(user_id)
        if not user:
            return {}
        return {
            "user_id": user.id,
            "username": user.username or "-",
            "date": user.created_at.strftime("%Y-%m-%d"),
            "lang": user.language.value.upper(),
            "generated": user.total_generated,
            "favorites": user.favorites_count,
            "referrals": user.referral_count,
            "coins": user.coins,
            "premium": "✅" if user.is_premium else "❌",
        }

    async def get_referral_link(self, user_id: int) -> str:
        user = await self.repo.get(user_id)
        if not user:
            return ""
        return f"https://t.me/{config.bot_name.replace(' ', '_')}?start=ref_{user.referral_code}"
