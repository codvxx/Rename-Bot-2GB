from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from app.core.exceptions import ValidationError
from app.core.validators import validate_caption_template


@Client.on_message(filters.private & filters.command("set_caption"))
async def set_caption_handler(client: Client, message: Message) -> None:
    if len(message.command) < 2:
        await message.reply_text(
            "Usage: /set_caption Your text here\n\nPlaceholders: {filename}, {filesize}, {duration}"
        )
        return
    try:
        template = validate_caption_template(message.text.split(None, 1)[1])
    except ValidationError as exc:
        await message.reply_text(str(exc))
        return
    await client.ctx.users.update_caption(message.from_user.id, template)
    await message.reply_text("Caption template saved.")


@Client.on_message(filters.private & filters.command("see_caption"))
async def see_caption_handler(client: Client, message: Message) -> None:
    settings = await client.ctx.users.get_user_settings(message.from_user.id)
    if not settings.caption_template:
        await message.reply_text("No caption template is configured.")
        return
    await message.reply_text(f"Saved caption template:\n<code>{settings.caption_template}</code>")


@Client.on_message(filters.private & filters.command("del_caption"))
async def delete_caption_handler(client: Client, message: Message) -> None:
    await client.ctx.users.update_caption(message.from_user.id, None)
    await message.reply_text("Caption template removed.")
