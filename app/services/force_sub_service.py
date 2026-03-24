from __future__ import annotations

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChannelInvalid, ChannelPrivate, ChatAdminRequired, UserNotParticipant, UsernameNotOccupied

from app.core.logging import get_logger

logger = get_logger(__name__)


class ForceSubscriptionService:
    def __init__(self, channels: tuple[str, ...]) -> None:
        self.channels = channels

    async def get_missing_channels(self, client, user_id: int) -> list[str]:
        missing = []
        for channel in self.channels:
            try:
                member = await client.get_chat_member(channel, user_id)
                if member.status == ChatMemberStatus.BANNED:
                    missing.append(channel)
            except UserNotParticipant:
                missing.append(channel)
            except (ChannelInvalid, ChannelPrivate, ChatAdminRequired, UsernameNotOccupied) as exc:
                logger.warning("Force subscribe check skipped for %s: %s", channel, exc)
                return []
        return missing
