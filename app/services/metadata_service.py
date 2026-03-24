from __future__ import annotations

import asyncio
from pathlib import Path

from app.core.exceptions import MediaProcessingError
from app.core.logging import get_logger

logger = get_logger(__name__)


class MetadataService:
    async def inject_metadata(self, source_path: Path, output_path: Path, metadata_text: str) -> Path:
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source_path),
            "-map",
            "0",
            "-c",
            "copy",
            "-metadata",
            f"title={metadata_text}",
            "-metadata",
            f"artist={metadata_text}",
            "-metadata",
            f"author={metadata_text}",
            str(output_path),
        ]
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0 or not output_path.exists():
            logger.warning("Metadata injection failed: %s", stderr.decode().strip())
            raise MediaProcessingError("Unable to inject metadata into this file")
        return output_path
