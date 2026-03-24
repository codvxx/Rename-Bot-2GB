from __future__ import annotations

import asyncio
import logging
import math
import shutil
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from pyrogram.types import Message

from app.core.exceptions import ValidationError


def utc_now() -> datetime:
    return datetime.utcnow()


def now_in_timezone(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def human_size(size: int | None) -> str:
    if not size:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    power = min(int(math.log(size, 1024)) if size > 0 else 0, len(units) - 1)
    value = size / (1024**power)
    return f"{value:.2f} {units[power]}"


def human_duration(seconds: int | None) -> str:
    total = max(int(seconds or 0), 0)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:d}:{secs:02d}"


def format_uptime(started_at: float) -> str:
    elapsed = max(int(time.monotonic() - started_at), 0)
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def create_job_id() -> str:
    return uuid.uuid4().hex[:12]


def cleanup_dir(path: Path | None) -> None:
    if path and path.exists():
        shutil.rmtree(path, ignore_errors=True)


def apply_prefix_suffix(filename: str, prefix: str | None, suffix: str | None) -> str:
    path = Path(filename)
    stem = path.stem
    ext = path.suffix
    prefix_part = prefix or ""
    suffix_part = suffix or ""
    return f"{prefix_part}{stem}{suffix_part}{ext}"


def render_caption(template: str | None, *, filename: str, filesize: int, duration: int | None) -> str:
    if not template:
        return filename
    try:
        return template.format(
            filename=filename,
            filesize=human_size(filesize),
            duration=human_duration(duration),
        )
    except Exception as exc:
        raise ValidationError("Your saved caption template is invalid. Please set it again.") from exc


def log_context(**fields: Any) -> str:
    return " ".join(f"{key}={value}" for key, value in fields.items() if value is not None)


@dataclass(slots=True)
class ProgressTracker:
    action: str
    message: Message
    logger: logging.Logger
    update_interval: float = 5.0
    started_at: float = field(default_factory=time.monotonic)
    _last_update: float = 0.0
    _last_text: str = ""
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def __call__(self, current: int, total: int) -> None:
        now = time.monotonic()
        if total <= 0:
            return
        if current != total and now - self._last_update < self.update_interval:
            return

        percent = current * 100 / total
        speed = current / max(now - self.started_at, 1)
        eta_seconds = int((total - current) / max(speed, 1))
        text = (
            f"{self.action}\n\n"
            f"Progress: {percent:.1f}%\n"
            f"Transferred: {human_size(current)} / {human_size(total)}\n"
            f"Speed: {human_size(int(speed))}/s\n"
            f"ETA: {human_duration(eta_seconds)}"
        )
        if text == self._last_text:
            return

        async with self._lock:
            try:
                await self.message.edit_text(text)
                self._last_update = now
                self._last_text = text
            except Exception as exc:
                self.logger.debug("Progress update skipped: %s", exc)
