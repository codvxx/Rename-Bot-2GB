from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, ForceReply, Message

from app.bot.keyboards.metadata import metadata_keyboard
from app.core.constants import METADATA_HELP_TEXT
from app.core.exceptions import ValidationError
from app.core.validators import sanitize_metadata_text


@Client.on_message(filters.private & filters.command("metadata"))
async def metadata_handler(client: Client, message: Message) -> None:
    settings = await client.ctx.users.get_user_settings(message.from_user.id)
    await message.reply_text(
        f"Metadata text: <code>{settings.metadata_text}</code>\nEnabled: {'Yes' if settings.metadata_enabled else 'No'}",
        reply_markup=metadata_keyboard(settings.metadata_enabled),
    )


@Client.on_callback_query(filters.regex(r"^metadata:"))
async def metadata_callback_handler(client: Client, query: CallbackQuery) -> None:
    action = query.data.split(":", 1)[1]
    settings = await client.ctx.users.get_user_settings(query.from_user.id)

    if action == "toggle":
        enabled = not settings.metadata_enabled
        await client.ctx.users.set_metadata_enabled(query.from_user.id, enabled)
        settings = await client.ctx.users.get_user_settings(query.from_user.id)
        await query.message.edit_text(
            f"Metadata text: <code>{settings.metadata_text}</code>\nEnabled: {'Yes' if settings.metadata_enabled else 'No'}",
            reply_markup=metadata_keyboard(settings.metadata_enabled),
        )
    elif action == "set":
        prompt = await query.message.reply_text(METADATA_HELP_TEXT, reply_markup=ForceReply(selective=True))
        client.ctx.metadata_prompt_sessions[prompt.id] = query.from_user.id
        await query.answer("Send the metadata text as a new message.")
        return
    await query.answer()


@Client.on_message(filters.private & filters.command("set_metadata_text"))
async def set_metadata_text_handler(client: Client, message: Message) -> None:
    if len(message.command) < 2:
        await message.reply_text("Usage: /set_metadata_text Your metadata text")
        return
    try:
        metadata_text = sanitize_metadata_text(message.text.split(None, 1)[1])
    except ValidationError as exc:
        await message.reply_text(str(exc))
        return
    await client.ctx.users.set_metadata_text(message.from_user.id, metadata_text)
    await message.reply_text("Metadata text saved.")


@Client.on_message(filters.private & filters.reply)
async def metadata_reply_handler(client: Client, message: Message) -> None:
    if not message.reply_to_message or not isinstance(message.reply_to_message.reply_markup, ForceReply):
        return
    owner_id = client.ctx.metadata_prompt_sessions.get(message.reply_to_message.id)
    if owner_id != message.from_user.id:
        return
    try:
        metadata_text = sanitize_metadata_text(message.text or "")
    except ValidationError as exc:
        await message.reply_text(str(exc))
        return
    await client.ctx.users.set_metadata_text(message.from_user.id, metadata_text)
    client.ctx.metadata_prompt_sessions.pop(message.reply_to_message.id, None)
    await message.reply_text("Metadata text saved.")
    try:
        await message.reply_to_message.delete()
    except Exception:
        pass
