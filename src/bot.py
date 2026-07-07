import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.config import config
from src.infrastructure.database import init_db
from src.infrastructure.cache import init_redis, close_redis
from src.infrastructure.scheduler import start_scheduler, stop_scheduler
from src.presentation.middlewares.throttling import ThrottlingMiddleware
from src.presentation.middlewares.maintenance import MaintenanceMiddleware
from src.presentation.middlewares.db import DbSessionMiddleware
from src.presentation.handlers import (
    start, admin, menu, nickname, favorites, search, language, bonus,
    referral, leaderboard, history, styler,
)

logger = logging.getLogger(__name__)

_bot: Bot | None = None
_dp: Dispatcher | None = None


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(styler.router)
    dp.include_router(menu.router)
    dp.include_router(nickname.router)
    dp.include_router(favorites.router)
    dp.include_router(search.router)
    dp.include_router(language.router)
    dp.include_router(bonus.router)
    dp.include_router(referral.router)
    dp.include_router(leaderboard.router)
    dp.include_router(history.router)

    dp.message.middleware(DbSessionMiddleware())
    dp.message.middleware(MaintenanceMiddleware())
    dp.message.middleware(ThrottlingMiddleware())

    dp.callback_query.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(MaintenanceMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())

    return dp


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(
            token=config.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


def get_dispatcher() -> Dispatcher:
    global _dp
    if _dp is None:
        _dp = create_dispatcher()
    return _dp


class BotApplication:
    def __init__(self):
        self.bot = get_bot()
        self.dp = get_dispatcher()

    async def start(self):
        logger.info("Initializing database...")
        await init_db()

        logger.info("Connecting to Redis...")
        try:
            await init_redis()
        except Exception as e:
            logger.warning("Redis unavailable: %s", e)

        logger.info("Starting scheduler...")
        try:
            await start_scheduler()
        except Exception as e:
            logger.warning("Scheduler unavailable: %s", e)

        logger.info("Removing webhook before polling...")
        await self.bot.delete_webhook(drop_pending_updates=True)

        logger.info("Starting bot polling...")
        await self.dp.start_polling(
            self.bot,
            allowed_updates=self.dp.resolve_used_update_types(),
        )

    async def stop(self):
        try:
            await stop_scheduler()
        except Exception:
            pass
        try:
            await close_redis()
        except Exception:
            pass
        try:
            await self.bot.session.close()
        except Exception:
            pass
        try:
            from src.infrastructure.database import engine
            await engine.dispose()
        except Exception:
            pass
