from pyrogram.types import BotCommand

BRAND_NAME = "IIUO Rename Bot"
BRAND_SHORT_NAME = "IIUO Renamer"
WELCOME_TEXT = (
    "Welcome to IIUO Rename Bot.\n\n"
    "Send a document, video, or audio file to rename it securely. "
    "You can also save a thumbnail, set a caption template, apply filename prefixes or suffixes, and enable metadata injection."
)
HELP_TEXT = (
    "Commands\n\n"
    "/start - Open the main menu\n"
    "/help - Show usage guidance\n"
    "/metadata - Manage metadata injection\n"
    "/set_caption - Save a custom caption template\n"
    "/see_caption - View your caption template\n"
    "/del_caption - Remove your caption template\n"
    "/set_prefix - Save a filename prefix\n"
    "/see_prefix - View your prefix\n"
    "/del_prefix - Remove your prefix\n"
    "/set_suffix - Save a filename suffix\n"
    "/see_suffix - View your suffix\n"
    "/del_suffix - Remove your suffix\n"
    "/view_thumb - View your saved thumbnail\n"
    "/del_thumb - Remove your thumbnail\n"
    "/ping - Check bot responsiveness\n\n"
    "Caption placeholders: {filename}, {filesize}, {duration}"
)
ABOUT_TEXT = (
    "IIUO Rename Bot is a production-focused Telegram media renaming platform built with Pyrogram and MongoDB.\n\n"
    "It is designed for safe file handling, flexible user preferences, and Render-friendly deployment."
)
METADATA_HELP_TEXT = (
    "Send the metadata text you want to inject.\n\n"
    "Example:\n"
    "Studio Release"
)

BOT_COMMANDS = [
    BotCommand("start", "Open the main menu"),
    BotCommand("help", "Show command usage"),
    BotCommand("metadata", "Manage metadata settings"),
    BotCommand("set_caption", "Set a caption template"),
    BotCommand("see_caption", "View your caption template"),
    BotCommand("del_caption", "Delete your caption template"),
    BotCommand("set_prefix", "Set a filename prefix"),
    BotCommand("see_prefix", "View your filename prefix"),
    BotCommand("del_prefix", "Delete your filename prefix"),
    BotCommand("set_suffix", "Set a filename suffix"),
    BotCommand("see_suffix", "View your filename suffix"),
    BotCommand("del_suffix", "Delete your filename suffix"),
    BotCommand("view_thumb", "View your saved thumbnail"),
    BotCommand("del_thumb", "Delete your saved thumbnail"),
    BotCommand("ping", "Check bot responsiveness"),
    BotCommand("stats", "Show admin statistics"),
    BotCommand("broadcast", "Broadcast a replied message"),
    BotCommand("restart", "Restart the bot"),
]
