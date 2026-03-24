from __future__ import annotations

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard(app_url: str | None) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("Help", callback_data="menu:help"),
            InlineKeyboardButton("About", callback_data="menu:about"),
        ],
        [InlineKeyboardButton("Settings", callback_data="menu:settings")],
    ]
    if app_url:
        rows.append([InlineKeyboardButton("Open Platform", url=app_url)])
    return InlineKeyboardMarkup(rows)


def close_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="menu:close")]])


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Metadata", callback_data="menu:metadata")],
            [InlineKeyboardButton("Back", callback_data="menu:start")],
        ]
    )
