from typing import Optional, List
from sqlalchemy import select, func, delete, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import User, Favorite, History, ForceChannel, Broadcast, BotSetting, ReferralLog, BonusLog, AdminLog
from src.domain.enums import Language, UserStatus


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int) -> Optional[User]:
        return await self.session.get(User, user_id)

    async def create(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None, referred_by: int = None) -> User:
        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            referred_by=referred_by,
            language=Language.UZBEK,
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def update(self, user_id: int, **kwargs):
        await self.session.execute(update(User).where(User.id == user_id).values(**kwargs))
        await self.session.commit()

    async def count(self, filters=None) -> int:
        query = select(func.count(User.id))
        if filters:
            query = query.where(filters)
        result = await self.session.execute(query)
        return result.scalar()

    async def all_ids(self) -> List[int]:
        result = await self.session.execute(select(User.id))
        return [row[0] for row in result]

    async def get_top_generators(self, limit: int = 10):
        result = await self.session.execute(
            select(User).order_by(User.total_generated.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_top_referrals(self, limit: int = 10):
        result = await self.session.execute(
            select(User).order_by(User.referral_count.desc()).limit(limit)
        )
        return result.scalars().all()

    async def search(self, query: str) -> List[User]:
        stmt = select(User).where(
            User.username.ilike(f"%{query}%") |
            User.first_name.ilike(f"%{query}%") |
            User.last_name.ilike(f"%{query}%")
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_favorites(self, user_id: int, offset: int = 0, limit: int = 10) -> List[Favorite]:
        result = await self.session.execute(
            select(Favorite).where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc()).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
        )
        return result.scalar()

    async def add(self, user_id: int, nickname: str, category: str) -> Favorite:
        fav = Favorite(user_id=user_id, nickname=nickname, category=category)
        self.session.add(fav)
        await self.session.commit()
        return fav

    async def exists(self, user_id: int, nickname: str) -> bool:
        result = await self.session.execute(
            select(Favorite).where(and_(Favorite.user_id == user_id, Favorite.nickname == nickname))
        )
        return result.scalar() is not None

    async def delete(self, fav_id: int):
        await self.session.execute(delete(Favorite).where(Favorite.id == fav_id))
        await self.session.commit()


class HistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user_id: int, nickname: str, category: str) -> History:
        entry = History(user_id=user_id, nickname=nickname, category=category)
        self.session.add(entry)
        await self.session.commit()
        return entry

    async def get_user_history(self, user_id: int, offset: int = 0, limit: int = 10) -> List[History]:
        result = await self.session.execute(
            select(History).where(History.user_id == user_id)
            .order_by(History.created_at.desc()).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(History.id)).where(History.user_id == user_id)
        )
        return result.scalar()

    async def clear_user_history(self, user_id: int):
        await self.session.execute(delete(History).where(History.user_id == user_id))
        await self.session.commit()


class ForceChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_channels(self) -> List[ForceChannel]:
        result = await self.session.execute(
            select(ForceChannel).where(ForceChannel.is_active == True).order_by(ForceChannel.position)
        )
        return result.scalars().all()

    async def get_all(self) -> List[ForceChannel]:
        result = await self.session.execute(
            select(ForceChannel).order_by(ForceChannel.position)
        )
        return result.scalars().all()

    async def add(self, channel_id: int, title: str, link: str, is_private: bool = False) -> ForceChannel:
        channel = ForceChannel(channel_id=channel_id, channel_title=title, channel_link=link, is_private=is_private)
        self.session.add(channel)
        await self.session.commit()
        return channel

    async def remove(self, channel_id: int):
        await self.session.execute(delete(ForceChannel).where(ForceChannel.id == channel_id))
        await self.session.commit()

    async def toggle(self, channel_id: int):
        ch = await self.session.get(ForceChannel, channel_id)
        if ch:
            ch.is_active = not ch.is_active
            await self.session.commit()


class BroadcastRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, admin_id: int, broadcast_type: str, content: str = None, file_id: str = None, caption: str = None) -> Broadcast:
        bc = Broadcast(admin_id=admin_id, broadcast_type=broadcast_type, content=content, file_id=file_id, caption=caption)
        self.session.add(bc)
        await self.session.commit()
        return bc

    async def count(self) -> int:
        result = await self.session.execute(select(func.count(Broadcast.id)))
        return result.scalar()

    async def get_recent(self, limit: int = 5):
        result = await self.session.execute(
            select(Broadcast).order_by(Broadcast.created_at.desc()).limit(limit)
        )
        return result.scalars().all()


class SettingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, key: str, default: str = None) -> Optional[str]:
        result = await self.session.execute(select(BotSetting).where(BotSetting.key == key))
        setting = result.scalar()
        return setting.value if setting else default

    async def set(self, key: str, value: str):
        result = await self.session.execute(select(BotSetting).where(BotSetting.key == key))
        setting = result.scalar()
        if setting:
            setting.value = value
        else:
            setting = BotSetting(key=key, value=value)
            self.session.add(setting)
        await self.session.commit()

    async def get_all(self) -> dict:
        result = await self.session.execute(select(BotSetting))
        return {s.key: s.value for s in result.scalars().all()}
