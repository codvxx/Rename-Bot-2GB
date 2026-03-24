from __future__ import annotations

from pyrogram.errors import RPCError

from app.core.constants import BOT_COMMANDS
from app.core.logging import get_logger
from app.core.utils import log_context, now_in_timezone

logger = get_logger(__name__)


def load_handlers() -> None:
    from app.bot.handlers import admin, caption, force_subscribe, metadata, prefix_suffix, rename, start, thumbnail  # noqa: F401


async def initialize_bot(client) -> None:
    me = await client.get_me()
    client.username = me.username or ""
    client.mention = me.mention
    client.bot_started_at = client.ctx.started_at
    await client.set_bot_commands(BOT_COMMANDS)

    timestamp = now_in_timezone(client.ctx.settings.default_timezone).isoformat()
    startup_text = (
        f"{client.ctx.settings.app_name} started successfully.\n"
        f"Time: {timestamp}\n"
        f"Admins: {len(client.ctx.settings.admin_ids)}\n"
        f"Health server: {client.ctx.settings.enable_health_server}"
    )

    logger.info("Bot startup complete %s", log_context(username=client.username, started_at=timestamp))

    try:
        await client.send_message(client.ctx.settings.log_channel_id, startup_text)
    except RPCError as exc:
        logger.warning("Unable to send startup log to channel: %s", exc)

    for admin_id in client.ctx.settings.admin_ids:
        try:
            await client.send_message(admin_id, startup_text)
        except RPCError:
            logger.debug("Startup notice skipped for admin_id=%s", admin_id)
