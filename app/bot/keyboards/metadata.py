from __future__ import annotations

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def metadata_keyboard(enabled: bool) -> InlineKeyboardMarkup:
    toggle_label = "Disable metadata" if enabled else "Enable metadata"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(toggle_label, callback_data="metadata:toggle")],
            [InlineKeyboardButton("Set metadata text", callback_data="metadata:set")],
            [InlineKeyboardButton("Back", callback_data="menu:settings")],
        ]
    )
