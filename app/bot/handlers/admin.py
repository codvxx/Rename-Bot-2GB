from __future__ import annotations

import os
import sys
import time

from pyrogram import Client, filters
from pyrogram.types import Message

from app.bot.filters.access import admin_filter
from app.core.logging import get_logger
from app.core.utils import format_uptime

logger = get_logger(__name__)


@Client.on_message(filters.private & filters.command("ping"))
async def ping_handler(client: Client, message: Message) -> None:
    started = time.perf_counter()
    reply = await message.reply_text("Pinging...")
    latency_ms = (time.perf_counter() - started) * 1000
    await reply.edit_text(f"Pong: {latency_ms:.2f} ms")


@Client.on_message(filters.private & filters.command("stats") & admin_filter)
async def stats_handler(client: Client, message: Message) -> None:
    total_users = await client.ctx.users.get_total_user_count()
    await message.reply_text(
        "System status\n\n"
        f"Uptime: {format_uptime(client.ctx.started_at)}\n"
        f"Users: {total_users}\n"
        f"Health server: {client.ctx.settings.enable_health_server}"
    )


@Client.on_message(filters.private & filters.command("broadcast") & admin_filter & filters.reply)
async def broadcast_handler(client: Client, message: Message) -> None:
    status = await message.reply_text("Broadcast started.")
    await client.ctx.broadcast_service.broadcast(client, message.reply_to_message, status)


@Client.on_message(filters.private & filters.command("restart") & admin_filter)
async def restart_handler(client: Client, message: Message) -> None:
    await message.reply_text("Restarting the worker.")
    logger.warning("Restart requested by admin_id=%s", message.from_user.id)
    os.execv(sys.executable, [sys.executable, "main.py"])
