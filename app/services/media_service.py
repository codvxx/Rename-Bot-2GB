from __future__ import annotations

import asyncio
from pathlib import Path

from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message

from app.core.logging import get_logger

logger = get_logger(__name__)


class MediaService:
    async def get_duration(self, source_path: Path, message: Message) -> int:
        media = getattr(message, message.media.value)
        if getattr(media, "duration", None):
            return int(media.duration)

        parser = createParser(str(source_path))
        if not parser:
            return 0
        try:
            metadata = extractMetadata(parser)
            if metadata and metadata.has("duration"):
                return int(metadata.get("duration").seconds)
        except Exception as exc:
            logger.debug("Duration extraction failed: %s", exc)
        finally:
            parser.close()
        return 0

    async def prepare_thumbnail(
        self,
        client,
        *,
        user_thumbnail_file_id: str | None,
        source_message: Message,
        source_path: Path,
        job_dir: Path,
        duration: int,
    ) -> Path | None:
        if user_thumbnail_file_id:
            target = job_dir / "thumb.jpg"
            downloaded = await client.download_media(user_thumbnail_file_id, file_name=str(target))
            if downloaded:
                return await self.normalize_thumbnail(Path(downloaded))

        if source_message.media == MessageMediaType.VIDEO:
            screenshot = await self.take_screenshot(source_path, job_dir, max(duration // 3, 1))
            if screenshot:
                return await self.normalize_thumbnail(screenshot)
        return None

    async def take_screenshot(self, source_path: Path, job_dir: Path, at_second: int) -> Path | None:
        output = job_dir / "screenshot.jpg"
        command = [
            "ffmpeg",
            "-y",
            "-ss",
            str(at_second),
            "-i",
            str(source_path),
            "-frames:v",
            "1",
            str(output),
        ]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return output if output.exists() else None

    async def normalize_thumbnail(self, path: Path) -> Path | None:
        try:
            with Image.open(path) as image:
                image = image.convert("RGB")
                image.thumbnail((320, 320))
                image.save(path, format="JPEG", quality=85)
            return path
        except Exception as exc:
            logger.warning("Thumbnail normalization failed: %s", exc)
            return None
