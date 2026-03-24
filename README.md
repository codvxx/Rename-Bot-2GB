# IIUO Rename Bot

## Overview
Production-ready Telegram file renaming bot built with Pyrogram, MongoDB, and FFmpeg.

## Features
- Fast file renaming
- Metadata injection
- Custom caption support
- Thumbnail management
- Prefix & suffix system
- Admin broadcast system
- Fully async architecture
- Render-ready deployment

## Architecture
- `app/bot` - Telegram client, handlers, filters, and keyboards
- `app/core` - config, validation, logging, and shared utilities
- `app/db` - MongoDB connection and user settings repository
- `app/services` - rename, media, metadata, thumbnail, and broadcast workflows
- `app/web` - optional health endpoint
- `main.py` - runtime entrypoint

## Deployment

### Render
- Deploy as a Background Worker
- Set the required environment variables
- Optionally enable the health server with `ENABLE_HEALTH_SERVER=true`

### Docker
```bash
docker build -t iiuo-rename-bot .
docker run -d --env-file .env iiuo-rename-bot
```

## Environment Variables

### Required
- `API_ID` - Telegram API ID from `my.telegram.org`
- `API_HASH` - Telegram API hash
- `BOT_TOKEN` - Bot token from BotFather
- `DATABASE_URL` - MongoDB connection string
- `DATABASE_NAME` - MongoDB database name
- `ADMIN_IDS` - Space or comma separated Telegram admin user IDs
- `LOG_CHANNEL_ID` - Telegram channel ID for startup and operational logs

### Optional
- `FORCE_SUBS` - Space or comma separated required channel usernames
- `START_PIC` - Telegram file ID or public image URL for the start screen
- `MAX_FILE_SIZE_MB` - Maximum accepted file size in MB
- `PORT` - Port used by the optional health server
- `ENABLE_HEALTH_SERVER` - Enable the health server on `0.0.0.0:$PORT`
- `DEFAULT_TIMEZONE` - Timezone used in startup logs
- `BROADCAST_BATCH_SIZE` - Number of users processed before a broadcast progress update
- `BROADCAST_SLEEP_SECONDS` - Pause between broadcast batches
- `WORKERS` - Pyrogram worker count
- `RENAME_TIMEOUT_SECONDS` - Timeout for rename interaction sessions
- `DOWNLOAD_DIR` - Base directory for downloads
- `TEMP_DIR` - Base directory for temporary rename jobs
- `APP_NAME` - Display name for the application
- `APP_URL` - Optional public project URL shown in the start menu

## Commands
- `/start` - Open the main menu
- `/help` - Show usage guidance
- `/metadata` - Manage metadata injection settings
- `/set_metadata_text` - Save custom metadata text
- `/set_caption` - Save a caption template
- `/see_caption` - View the current caption template
- `/del_caption` - Delete the current caption template
- `/set_prefix` - Save a filename prefix
- `/see_prefix` - View the current prefix
- `/del_prefix` - Delete the current prefix
- `/set_suffix` - Save a filename suffix
- `/see_suffix` - View the current suffix
- `/del_suffix` - Delete the current suffix
- `/view_thumb` - View the saved thumbnail
- `/del_thumb` - Delete the saved thumbnail
- `/ping` - Check bot responsiveness
- `/stats` - Show admin stats
- `/broadcast` - Broadcast a replied message to all users
- `/restart` - Restart the worker process

## Security
- No hardcoded secrets
- Env-based config
- Safe file handling
- Filename sanitization for user-controlled input
- Isolated temp directories with cleanup on success and failure

## License
MIT
