import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import config
from src.bot import BotApplication


def setup_logging():
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


async def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting NickForge AI Bot...")

    app = BotApplication()

    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
    finally:
        await app.stop()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
