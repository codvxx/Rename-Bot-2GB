from __future__ import annotations

import time

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, ForceReply, Message

from app.bot.client import RenameChoiceSession, RenamePromptSession
from app.bot.keyboards.rename import output_mode_keyboard
from app.core.exceptions import ValidationError
from app.core.logging import get_logger
from app.core.validators import sanitize_filename, validate_file_size

logger = get_logger(__name__)


def _get_media(message: Message):
    return getattr(message, message.media.value)


@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def rename_start_handler(client: Client, message: Message) -> None:
    media = _get_media(message)
    try:
        validate_file_size(getattr(media, "file_size", None), client.ctx.settings.max_file_size_bytes)
    except ValidationError as exc:
        await message.reply_text(str(exc))
        return
    prompt = await message.reply_text(
        f"Send the new filename for <code>{media.file_name or 'your file'}</code>",
        reply_markup=ForceReply(selective=True),
    )
    client.ctx.rename_prompt_sessions[prompt.id] = RenamePromptSession(
        source_message_id=message.id,
        source_chat_id=message.chat.id,
    )


@Client.on_message(filters.private & filters.reply)
async def rename_filename_reply_handler(client: Client, message: Message) -> None:
    if not message.reply_to_message or not isinstance(message.reply_to_message.reply_markup, ForceReply):
        return

    session = client.ctx.rename_prompt_sessions.get(message.reply_to_message.id)
    if not session:
        return

    if time.monotonic() - session.created_at > client.ctx.settings.rename_timeout_seconds:
        client.ctx.rename_prompt_sessions.pop(message.reply_to_message.id, None)
        await message.reply_text("That rename prompt has expired. Send the file again to start a new rename.")
        return

    source_message = await client.get_messages(session.source_chat_id, session.source_message_id)
    media = _get_media(source_message)
    default_extension = (media.file_name or "file.bin").rsplit(".", 1)[-1] if "." in (media.file_name or "") else "bin"

    try:
        target_name = sanitize_filename(message.text or "", default_extension=f".{default_extension}")
    except ValidationError as exc:
        await message.reply_text(str(exc))
        return

    modes = client.ctx.rename_service.available_output_modes(source_message)
    chooser = await message.reply_text(
        f"Choose the output type for <code>{target_name}</code>",
        reply_markup=output_mode_keyboard(message.reply_to_message.id, modes),
    )
    client.ctx.rename_choice_sessions[chooser.id] = RenameChoiceSession(
        source_message_id=session.source_message_id,
        source_chat_id=session.source_chat_id,
        target_name=target_name,
    )
    client.ctx.rename_prompt_sessions.pop(message.reply_to_message.id, None)
    try:
        await message.reply_to_message.delete()
    except Exception:
        logger.debug("Prompt cleanup skipped")


@Client.on_callback_query(filters.regex(r"^rename:"))
async def rename_output_handler(client: Client, query: CallbackQuery) -> None:
    _, message_id_text, action = query.data.split(":", 2)
    choice_session = client.ctx.rename_choice_sessions.get(query.message.id)
    if not choice_session:
        await query.answer("This rename request has expired.", show_alert=True)
        return
    if time.monotonic() - choice_session.created_at > client.ctx.settings.rename_timeout_seconds:
        client.ctx.rename_choice_sessions.pop(query.message.id, None)
        await query.message.edit_text("This rename request has expired.")
        await query.answer()
        return
    if action == "cancel":
        client.ctx.rename_choice_sessions.pop(query.message.id, None)
        await query.message.edit_text("Rename request cancelled.")
        await query.answer()
        return

    source_message = await client.get_messages(choice_session.source_chat_id, choice_session.source_message_id)
    if not source_message.from_user or source_message.from_user.id != query.from_user.id:
        await query.answer("Only the original sender can complete this rename.", show_alert=True)
        return
    if source_message.id != choice_session.source_message_id:
        await query.answer("Original file could not be found.", show_alert=True)
        return

    if action not in client.ctx.rename_service.available_output_modes(source_message):
        await query.answer("That output type is not available for this file.", show_alert=True)
        return

    user_settings = await client.ctx.users.get_user_settings(query.from_user.id)
    result = None
    async with client.ctx.rename_semaphore:
        try:
            await query.message.edit_text("Preparing rename job...")
            result = await client.ctx.rename_service.process(
                client,
                source_message=source_message,
                raw_filename=choice_session.target_name,
                output_mode=action,
                user_settings=user_settings,
                status_message=query.message,
            )
            await client.ctx.rename_service.upload_result(
                client,
                chat_id=query.message.chat.id,
                source_message=source_message,
                result=result,
                user_settings=user_settings,
                output_mode=action,
                status_message=query.message,
            )
            await query.message.delete()
        except ValidationError as exc:
            await query.message.edit_text(str(exc))
        except Exception as exc:
            logger.exception("Rename flow failed: %s", exc)
            await query.message.edit_text("Rename failed. Please try again with a supported media file.")
        finally:
            client.ctx.rename_choice_sessions.pop(query.message.id, None)
            client.ctx.rename_service.cleanup(result)
    await query.answer()
