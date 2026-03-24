from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from app.bot.keyboards.common import close_keyboard, settings_keyboard, start_keyboard
from app.core.constants import ABOUT_TEXT, HELP_TEXT, WELCOME_TEXT
from app.core.logging import get_logger
from app.core.utils import human_size

logger = get_logger(__name__)


async def _welcome_text(client: Client, user_id: int) -> str:
    settings = await client.ctx.users.get_user_settings(user_id)
    return (
        f"{WELCOME_TEXT}\n\n"
        f"Current limits\n"
        f"- Max file size: {human_size(client.ctx.settings.max_file_size_bytes)}\n"
        f"- Metadata enabled: {'Yes' if settings.metadata_enabled else 'No'}"
    )


@Client.on_message(filters.private & filters.command(["start", "help"]))
async def start_handler(client: Client, message: Message) -> None:
    await client.ctx.users.create_user_if_not_exists(message.from_user.id)
    text = await _welcome_text(client, message.from_user.id)
    if client.ctx.settings.start_pic:
        await message.reply_photo(
            client.ctx.settings.start_pic,
            caption=text,
            reply_markup=start_keyboard(client.ctx.settings.app_url),
        )
        return
    await message.reply_text(text, reply_markup=start_keyboard(client.ctx.settings.app_url))


@Client.on_callback_query(filters.regex(r"^menu:"))
async def menu_callback_handler(client: Client, query: CallbackQuery) -> None:
    await client.ctx.users.create_user_if_not_exists(query.from_user.id)
    action = query.data.split(":", 1)[1]
    if action == "start":
        await query.message.edit_text(
            await _welcome_text(client, query.from_user.id),
            reply_markup=start_keyboard(client.ctx.settings.app_url),
        )
    elif action == "help":
        await query.message.edit_text(HELP_TEXT, reply_markup=close_keyboard())
    elif action == "about":
        await query.message.edit_text(ABOUT_TEXT, reply_markup=close_keyboard())
    elif action == "settings":
        await query.message.edit_text("Open a settings panel.", reply_markup=settings_keyboard())
    elif action == "metadata":
        settings = await client.ctx.users.get_user_settings(query.from_user.id)
        from app.bot.keyboards.metadata import metadata_keyboard

        await query.message.edit_text(
            f"Metadata text: <code>{settings.metadata_text}</code>\nEnabled: {'Yes' if settings.metadata_enabled else 'No'}",
            reply_markup=metadata_keyboard(settings.metadata_enabled),
        )
    elif action == "close":
        await query.message.delete()
    await query.answer()
