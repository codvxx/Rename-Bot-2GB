from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.private & filters.photo)
async def save_thumbnail_handler(client: Client, message: Message) -> None:
    await client.ctx.users.create_user_if_not_exists(message.from_user.id)
    await client.ctx.thumbnail_service.save_thumbnail(message.from_user.id, message.photo.file_id)
    await message.reply_text("Thumbnail saved.")


@Client.on_message(filters.private & filters.command("view_thumb"))
async def view_thumbnail_handler(client: Client, message: Message) -> None:
    settings = await client.ctx.users.get_user_settings(message.from_user.id)
    if not settings.thumbnail_file_id:
        await message.reply_text("No thumbnail is saved.")
        return
    await client.send_photo(message.chat.id, settings.thumbnail_file_id)


@Client.on_message(filters.private & filters.command("del_thumb"))
async def delete_thumbnail_handler(client: Client, message: Message) -> None:
    await client.ctx.thumbnail_service.clear_thumbnail(message.from_user.id)
    await message.reply_text("Thumbnail removed.")
