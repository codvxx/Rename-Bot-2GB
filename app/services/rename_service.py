from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyrogram.enums import MessageMediaType
from pyrogram.types import Message

from app.core.exceptions import MediaProcessingError
from app.core.logging import get_logger
from app.core.utils import ProgressTracker, apply_prefix_suffix, create_job_id, log_context, render_caption
from app.core.validators import sanitize_filename, validate_file_size
from app.db.models import UserSettings
from app.services.file_service import FileService
from app.services.media_service import MediaService
from app.services.metadata_service import MetadataService

logger = get_logger(__name__)


@dataclass(slots=True)
class RenameResult:
    filename: str
    output_path: Path
    thumbnail_path: Path | None
    duration: int
    file_size: int
    job_id: str


class RenameService:
    def __init__(
        self,
        *,
        file_service: FileService,
        media_service: MediaService,
        metadata_service: MetadataService,
        max_file_size_bytes: int,
    ) -> None:
        self.file_service = file_service
        self.media_service = media_service
        self.metadata_service = metadata_service
        self.max_file_size_bytes = max_file_size_bytes

    async def process(
        self,
        client,
        *,
        source_message: Message,
        raw_filename: str,
        output_mode: str,
        user_settings: UserSettings,
        status_message: Message,
    ) -> RenameResult:
        media = getattr(source_message, source_message.media.value)
        validate_file_size(getattr(media, "file_size", None), self.max_file_size_bytes)
        default_extension = Path(media.file_name or "file.bin").suffix
        target_filename = sanitize_filename(raw_filename, default_extension=default_extension)
        target_filename = sanitize_filename(
            apply_prefix_suffix(target_filename, user_settings.prefix, user_settings.suffix),
            default_extension=default_extension,
        )

        job_id = create_job_id()
        job_dir = self.file_service.create_job_dir(source_message.from_user.id, job_id)
        source_path = job_dir / (sanitize_filename(media.file_name or f"source{default_extension}") or f"source{default_extension}")
        output_path = job_dir / target_filename
        processed_path = output_path
        thumbnail_path = None
        logger.info("Rename job started %s", log_context(user_id=source_message.from_user.id, job_id=job_id))

        try:
            await status_message.edit_text("Downloading file...")
            download_progress = ProgressTracker("Downloading file...", status_message, logger)
            downloaded = await client.download_media(
                source_message,
                file_name=str(source_path),
                progress=download_progress,
            )
            if not downloaded:
                raise MediaProcessingError("Download failed")

            source_path = Path(downloaded)
            if source_path != output_path:
                source_path.rename(output_path)
            processed_path = output_path

            duration = await self.media_service.get_duration(processed_path, source_message)

            if user_settings.metadata_enabled:
                await status_message.edit_text("Applying metadata...")
                metadata_output = job_dir / f"meta_{target_filename}"
                try:
                    processed_path = await self.metadata_service.inject_metadata(
                        processed_path,
                        metadata_output,
                        user_settings.metadata_text,
                    )
                except MediaProcessingError:
                    logger.warning(
                        "Metadata skipped %s",
                        log_context(user_id=source_message.from_user.id, job_id=job_id),
                    )

            await status_message.edit_text("Preparing thumbnail...")
            thumbnail_path = await self.media_service.prepare_thumbnail(
                client,
                user_thumbnail_file_id=user_settings.thumbnail_file_id,
                source_message=source_message,
                source_path=processed_path,
                job_dir=job_dir,
                duration=duration,
            )

            return RenameResult(
                filename=target_filename,
                output_path=processed_path,
                thumbnail_path=thumbnail_path,
                duration=duration,
                file_size=processed_path.stat().st_size,
                job_id=job_id,
            )
        except Exception:
            self.file_service.cleanup_job_dir(job_dir)
            raise

    async def upload_result(
        self,
        client,
        *,
        chat_id: int,
        source_message: Message,
        result: RenameResult,
        user_settings: UserSettings,
        output_mode: str,
        status_message: Message,
    ) -> None:
        caption = render_caption(
            user_settings.caption_template,
            filename=result.filename,
            filesize=result.file_size,
            duration=result.duration,
        )
        upload_progress = ProgressTracker("Uploading file...", status_message, logger)

        if output_mode == "document":
            await client.send_document(
                chat_id,
                document=str(result.output_path),
                thumb=str(result.thumbnail_path) if result.thumbnail_path else None,
                caption=caption,
                progress=upload_progress,
            )
            return

        if output_mode == "video":
            await client.send_video(
                chat_id,
                video=str(result.output_path),
                duration=result.duration or None,
                thumb=str(result.thumbnail_path) if result.thumbnail_path else None,
                caption=caption,
                progress=upload_progress,
            )
            return

        if output_mode == "audio":
            await client.send_audio(
                chat_id,
                audio=str(result.output_path),
                duration=result.duration or None,
                thumb=str(result.thumbnail_path) if result.thumbnail_path else None,
                caption=caption,
                progress=upload_progress,
            )
            return

        raise MediaProcessingError(f"Unsupported output mode: {output_mode}")

    def cleanup(self, result: RenameResult | None) -> None:
        if result is not None:
            self.file_service.cleanup_job_dir(result.output_path.parent)

    @staticmethod
    def available_output_modes(source_message: Message) -> list[str]:
        if source_message.media == MessageMediaType.AUDIO:
            return ["document", "audio"]
        if source_message.media == MessageMediaType.VIDEO:
            return ["document", "video"]
        document = source_message.document
        mime_type = (document.mime_type or "").lower() if document else ""
        if mime_type.startswith("audio/"):
            return ["document", "audio"]
        if mime_type.startswith("video/"):
            return ["document", "video"]
        return ["document"]
