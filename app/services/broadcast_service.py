from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field

from pyrogram.errors import FloodWait, InputUserDeactivated, PeerIdInvalid, UserIsBlocked
from pyrogram.types import Message

from app.core.config import Settings
from app.db.users import UserRepository


@dataclass(slots=True)
class BroadcastSummary:
    total: int = 0
    processed: int = 0
    success: int = 0
    failed: int = 0
    deleted: int = 0
    started_at: float = field(default_factory=time.monotonic)


class BroadcastService:
    def __init__(self, users: UserRepository, settings: Settings, logger: logging.Logger) -> None:
        self.users = users
        self.settings = settings
        self.logger = logger

    async def broadcast(self, client, source_message: Message, status_message: Message) -> BroadcastSummary:
        summary = BroadcastSummary(total=await self.users.get_total_user_count(), started_at=time.monotonic())
        async for user in self.users.iter_all_users():
            summary.processed += 1
            result = await self._send_with_retry(client, user.user_id, source_message)
            if result == "success":
                summary.success += 1
            elif result == "deleted":
                summary.failed += 1
                summary.deleted += 1
                await self.users.delete_user(user.user_id)
            else:
                summary.failed += 1

            if summary.processed % self.settings.broadcast_batch_size == 0:
                await status_message.edit_text(self._progress_text(summary))
                await asyncio.sleep(self.settings.broadcast_sleep_seconds)

        await status_message.edit_text(self._final_text(summary))
        return summary

    async def _send_with_retry(self, client, user_id: int, source_message: Message) -> str:
        while True:
            try:
                await source_message.copy(chat_id=user_id)
                return "success"
            except FloodWait as exc:
                self.logger.warning("Broadcast flood wait user_id=%s wait=%s", user_id, exc.value)
                await asyncio.sleep(exc.value)
            except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
                self.logger.info("Removing unreachable user user_id=%s", user_id)
                return "deleted"
            except Exception as exc:
                self.logger.error("Broadcast failed user_id=%s error=%s", user_id, exc)
                return "failed"

    def _progress_text(self, summary: BroadcastSummary) -> str:
        return (
            "Broadcast in progress\n\n"
            f"Users: {summary.total}\n"
            f"Processed: {summary.processed}\n"
            f"Delivered: {summary.success}\n"
            f"Failed: {summary.failed}\n"
            f"Removed: {summary.deleted}"
        )

    def _final_text(self, summary: BroadcastSummary) -> str:
        duration = int(time.monotonic() - summary.started_at)
        return (
            "Broadcast finished\n\n"
            f"Users: {summary.total}\n"
            f"Processed: {summary.processed}\n"
            f"Delivered: {summary.success}\n"
            f"Failed: {summary.failed}\n"
            f"Removed: {summary.deleted}\n"
            f"Duration: {duration}s"
        )
