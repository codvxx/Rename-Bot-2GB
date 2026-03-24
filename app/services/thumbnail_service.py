from __future__ import annotations

from app.db.users import UserRepository


class ThumbnailService:
    def __init__(self, users: UserRepository) -> None:
        self.users = users

    async def save_thumbnail(self, user_id: int, file_id: str) -> None:
        await self.users.update_thumbnail(user_id, file_id)

    async def clear_thumbnail(self, user_id: int) -> None:
        await self.users.update_thumbnail(user_id, None)
