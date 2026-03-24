from __future__ import annotations

import asyncio

from aiohttp import web
from pyrogram import idle

from app.bot.client import AppContext, RenameBot
from app.bot.startup import initialize_bot, load_handlers
from app.core.config import load_settings
from app.core.logging import configure_logging, get_logger
from app.db.mongo import MongoManager
from app.db.users import UserRepository
from app.services.broadcast_service import BroadcastService
from app.services.file_service import FileService
from app.services.force_sub_service import ForceSubscriptionService
from app.services.media_service import MediaService
from app.services.metadata_service import MetadataService
from app.services.rename_service import RenameService
from app.services.thumbnail_service import ThumbnailService
from app.web.app import create_web_app

logger = get_logger(__name__)


async def start_health_server(settings):
    app = create_web_app(settings)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=settings.port)
    await site.start()
    logger.info("Health server started on port %s", settings.port)
    return runner


async def main() -> None:
    configure_logging()
    settings = load_settings()
    logger.info("Configuration loaded for %s", settings.app_name)

    mongo = MongoManager(settings)
    await mongo.connect()
    await mongo.ping()

    users = UserRepository(mongo.database["users"])
    await users.ensure_indexes()

    file_service = FileService(settings)
    metadata_service = MetadataService()
    media_service = MediaService()
    rename_service = RenameService(
        file_service=file_service,
        media_service=media_service,
        metadata_service=metadata_service,
        max_file_size_bytes=settings.max_file_size_bytes,
    )
    thumbnail_service = ThumbnailService(users)
    force_sub_service = ForceSubscriptionService(settings.force_subs)
    broadcast_service = BroadcastService(users, settings, logger)

    context = AppContext(
        settings=settings,
        users=users,
        file_service=file_service,
        metadata_service=metadata_service,
        media_service=media_service,
        rename_service=rename_service,
        thumbnail_service=thumbnail_service,
        force_sub_service=force_sub_service,
        broadcast_service=broadcast_service,
    )

    load_handlers()
    bot = RenameBot(settings, context)
    health_runner = None

    try:
        await bot.start()
        await initialize_bot(bot)
        if settings.enable_health_server:
            health_runner = await start_health_server(settings)
        await idle()
    finally:
        if health_runner is not None:
            await health_runner.cleanup()
        if bot.is_connected:
            await bot.stop()
        await mongo.close()


if __name__ == "__main__":
    asyncio.run(main())
