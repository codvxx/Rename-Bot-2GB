from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import Message

from app.core.exceptions import ValidationError
from app.core.validators import sanitize_affix


@Client.on_message(filters.private & filters.command("set_prefix"))
async def set_prefix_handler(client: Client, message: Message) -> None:
    if len(message.command) < 2:
        await message.reply_text("Usage: /set_prefix value")
        return
    try:
        prefix = sanitize_affix(message.text.split(None, 1)[1], field_name="Prefix")
    except ValidationError as exc:
        await message.reply_text(str(exc))
        return
    await client.ctx.users.update_prefix(message.from_user.id, prefix)
    await message.reply_text("Prefix saved.")


@Client.on_message(filters.private & filters.command("see_prefix"))
async def see_prefix_handler(client: Client, message: Message) -> None:
    settings = await client.ctx.users.get_user_settings(message.from_user.id)
    await message.reply_text(f"Current prefix: <code>{settings.prefix or 'Not set'}</code>")


@Client.on_message(filters.private & filters.command("del_prefix"))
async def delete_prefix_handler(client: Client, message: Message) -> None:
    await client.ctx.users.update_prefix(message.from_user.id, None)
    await message.reply_text("Prefix removed.")


@Client.on_message(filters.private & filters.command("set_suffix"))
async def set_suffix_handler(client: Client, message: Message) -> None:
    if len(message.command) < 2:
        await message.reply_text("Usage: /set_suffix value")
        return
    try:
        suffix = sanitize_affix(message.text.split(None, 1)[1], field_name="Suffix")
    except ValidationError as exc:
        await message.reply_text(str(exc))
        return
    await client.ctx.users.update_suffix(message.from_user.id, suffix)
    await message.reply_text("Suffix saved.")


@Client.on_message(filters.private & filters.command("see_suffix"))
async def see_suffix_handler(client: Client, message: Message) -> None:
    settings = await client.ctx.users.get_user_settings(message.from_user.id)
    await message.reply_text(f"Current suffix: <code>{settings.suffix or 'Not set'}</code>")


@Client.on_message(filters.private & filters.command("del_suffix"))
async def delete_suffix_handler(client: Client, message: Message) -> None:
    await client.ctx.users.update_suffix(message.from_user.id, None)
    await message.reply_text("Suffix removed.")
