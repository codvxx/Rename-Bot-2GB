from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MongoManager:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncIOMotorClient | None = None
        self._database: AsyncIOMotorDatabase | None = None

    @property
    def database(self) -> AsyncIOMotorDatabase:
        if self._database is None:
            raise RuntimeError("MongoDB is not connected")
        return self._database

    async def connect(self) -> AsyncIOMotorDatabase:
        self._client = AsyncIOMotorClient(self._settings.database_url, serverSelectionTimeoutMS=10000)
        self._database = self._client[self._settings.database_name]
        logger.info("MongoDB client initialized")
        return self._database

    async def ping(self) -> None:
        await self.database.command("ping")
        logger.info("MongoDB connectivity check passed")

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            logger.info("MongoDB connection closed")
