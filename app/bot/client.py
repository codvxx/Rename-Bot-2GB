from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

from pyrogram import Client
from pyrogram.enums import ParseMode

from app.core.config import Settings
from app.db.users import UserRepository
from app.services.broadcast_service import BroadcastService
from app.services.file_service import FileService
from app.services.force_sub_service import ForceSubscriptionService
from app.services.media_service import MediaService
from app.services.metadata_service import MetadataService
from app.services.rename_service import RenameService
from app.services.thumbnail_service import ThumbnailService


@dataclass(slots=True)
class RenamePromptSession:
    source_message_id: int
    source_chat_id: int
    created_at: float = field(default_factory=time.monotonic)


@dataclass(slots=True)
class RenameChoiceSession:
    source_message_id: int
    source_chat_id: int
    target_name: str
    created_at: float = field(default_factory=time.monotonic)


@dataclass(slots=True)
class AppContext:
    settings: Settings
    users: UserRepository
    file_service: FileService
    metadata_service: MetadataService
    media_service: MediaService
    rename_service: RenameService
    thumbnail_service: ThumbnailService
    force_sub_service: ForceSubscriptionService
    broadcast_service: BroadcastService
    started_at: float = field(default_factory=time.monotonic)
    rename_prompt_sessions: dict[int, RenamePromptSession] = field(default_factory=dict)
    rename_choice_sessions: dict[int, RenameChoiceSession] = field(default_factory=dict)
    metadata_prompt_sessions: dict[int, int] = field(default_factory=dict)
    rename_semaphore: asyncio.Semaphore = field(default_factory=lambda: asyncio.Semaphore(2))


class RenameBot(Client):
    def __init__(self, settings: Settings, context: AppContext) -> None:
        super().__init__(
            name="iiuo_renamer",
            api_id=settings.api_id,
            api_hash=settings.api_hash,
            bot_token=settings.bot_token,
            workers=settings.workers,
            parse_mode=ParseMode.HTML,
            sleep_threshold=30,
        )
        self.ctx = context
        self.bot_started_at = time.monotonic()
        self.username = ""
        self.mention = settings.app_name
