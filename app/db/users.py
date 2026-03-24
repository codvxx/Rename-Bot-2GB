from __future__ import annotations

from datetime import datetime
from typing import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.utils import utc_now
from app.db.models import UserSettings


class UserRepository:
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def ensure_indexes(self) -> None:
        await self.collection.create_index("updated_at")

    async def create_user_if_not_exists(self, user_id: int) -> UserSettings:
        now = utc_now()
        defaults = UserSettings(user_id=user_id, created_at=now, updated_at=now).to_document()
        await self.collection.update_one(
            {"_id": user_id},
            {
                "$setOnInsert": defaults,
                "$set": {"updated_at": now},
            },
            upsert=True,
        )
        return await self.get_user_settings(user_id)

    async def get_user_settings(self, user_id: int) -> UserSettings:
        document = await self.collection.find_one({"_id": user_id})
        if not document:
            return await self.create_user_if_not_exists(user_id)
        return UserSettings.from_document(document)

    async def update_thumbnail(self, user_id: int, file_id: str | None) -> None:
        await self._update_fields(user_id, {"thumbnail_file_id": file_id})

    async def update_caption(self, user_id: int, caption: str | None) -> None:
        await self._update_fields(user_id, {"caption_template": caption})

    async def update_prefix(self, user_id: int, prefix: str | None) -> None:
        await self._update_fields(user_id, {"prefix": prefix})

    async def update_suffix(self, user_id: int, suffix: str | None) -> None:
        await self._update_fields(user_id, {"suffix": suffix})

    async def set_metadata_enabled(self, user_id: int, enabled: bool) -> None:
        await self._update_fields(user_id, {"metadata_enabled": enabled})

    async def set_metadata_text(self, user_id: int, text: str) -> None:
        await self._update_fields(user_id, {"metadata_text": text})

    async def get_total_user_count(self) -> int:
        return await self.collection.count_documents({})

    async def iter_all_users(self) -> AsyncIterator[UserSettings]:
        async for document in self.collection.find({}, projection={"_id": True}):
            yield UserSettings.from_document(document)

    async def delete_user(self, user_id: int) -> None:
        await self.collection.delete_one({"_id": user_id})

    async def _update_fields(self, user_id: int, fields: dict[str, object]) -> None:
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": {**fields, "updated_at": utc_now()}, "$setOnInsert": {"created_at": utc_now()}},
            upsert=True,
        )
