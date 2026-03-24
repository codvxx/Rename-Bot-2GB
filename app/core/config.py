from __future__ import annotations

import os
from dataclasses import dataclass

from app.core.validators import (
    ensure_directory,
    parse_admin_ids,
    parse_bool,
    parse_force_subs,
    parse_int,
    parse_positive_int,
    require_env,
)


@dataclass(slots=True)
class Settings:
    api_id: int
    api_hash: str
    bot_token: str
    database_url: str
    database_name: str
    admin_ids: tuple[int, ...]
    log_channel_id: int
    force_subs: tuple[str, ...]
    start_pic: str | None
    max_file_size_mb: int
    port: int
    enable_health_server: bool
    default_timezone: str
    broadcast_batch_size: int
    broadcast_sleep_seconds: int
    workers: int
    rename_timeout_seconds: int
    download_dir: str
    temp_dir: str
    app_name: str
    app_url: str | None

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


def load_settings() -> Settings:
    max_file_size_mb = parse_positive_int(os.getenv("MAX_FILE_SIZE_MB"), "MAX_FILE_SIZE_MB", default=2048)
    download_dir = ensure_directory(os.getenv("DOWNLOAD_DIR", "./data/downloads"))
    temp_dir = ensure_directory(os.getenv("TEMP_DIR", "./data/temp"))

    return Settings(
        api_id=parse_int(os.getenv("API_ID"), "API_ID"),
        api_hash=require_env(os.getenv("API_HASH"), "API_HASH"),
        bot_token=require_env(os.getenv("BOT_TOKEN"), "BOT_TOKEN"),
        database_url=require_env(os.getenv("DATABASE_URL"), "DATABASE_URL"),
        database_name=require_env(os.getenv("DATABASE_NAME"), "DATABASE_NAME"),
        admin_ids=parse_admin_ids(os.getenv("ADMIN_IDS")),
        log_channel_id=parse_int(os.getenv("LOG_CHANNEL_ID"), "LOG_CHANNEL_ID"),
        force_subs=parse_force_subs(os.getenv("FORCE_SUBS")),
        start_pic=os.getenv("START_PIC") or None,
        max_file_size_mb=max_file_size_mb,
        port=parse_positive_int(os.getenv("PORT"), "PORT", default=10000),
        enable_health_server=parse_bool(os.getenv("ENABLE_HEALTH_SERVER"), default=False),
        default_timezone=os.getenv("DEFAULT_TIMEZONE", "UTC").strip() or "UTC",
        broadcast_batch_size=parse_positive_int(
            os.getenv("BROADCAST_BATCH_SIZE"), "BROADCAST_BATCH_SIZE", default=25
        ),
        broadcast_sleep_seconds=parse_positive_int(
            os.getenv("BROADCAST_SLEEP_SECONDS"), "BROADCAST_SLEEP_SECONDS", default=2
        ),
        workers=parse_positive_int(os.getenv("WORKERS"), "WORKERS", default=100),
        rename_timeout_seconds=parse_positive_int(
            os.getenv("RENAME_TIMEOUT_SECONDS"), "RENAME_TIMEOUT_SECONDS", default=900
        ),
        download_dir=download_dir,
        temp_dir=temp_dir,
        app_name=os.getenv("APP_NAME", "IIUO Rename Bot").strip() or "IIUO Rename Bot",
        app_url=os.getenv("APP_URL") or None,
    )
