from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


@Client.on_message(filters.private, group=-10)
async def force_subscribe_handler(client: Client, message: Message) -> None:
    if not message.from_user or message.from_user.is_bot:
        return
    await client.ctx.users.create_user_if_not_exists(message.from_user.id)
    missing_channels = await client.ctx.force_sub_service.get_missing_channels(client, message.from_user.id)
    if not missing_channels:
        return

    buttons = [[InlineKeyboardButton(f"Join @{channel}", url=f"https://t.me/{channel}")] for channel in missing_channels]
    await message.reply_text(
        "Please join the required update channel before using the bot.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    message.stop_propagation()
