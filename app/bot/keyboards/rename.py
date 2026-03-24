from __future__ import annotations

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def output_mode_keyboard(message_id: int, modes: list[str]) -> InlineKeyboardMarkup:
    labels = {
        "document": "Document",
        "video": "Video",
        "audio": "Audio",
    }
    rows = [[InlineKeyboardButton(labels[mode], callback_data=f"rename:{message_id}:{mode}")] for mode in modes]
    rows.append([InlineKeyboardButton("Cancel", callback_data=f"rename:{message_id}:cancel")])
    return InlineKeyboardMarkup(rows)
