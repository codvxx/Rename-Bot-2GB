from __future__ import annotations

import tempfile
from pathlib import Path

from app.core.config import Settings
from app.core.utils import cleanup_dir


class FileService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.download_root = Path(settings.download_dir)
        self.temp_root = Path(settings.temp_dir)
        self.download_root.mkdir(parents=True, exist_ok=True)
        self.temp_root.mkdir(parents=True, exist_ok=True)

    def create_job_dir(self, user_id: int, job_id: str) -> Path:
        prefix = f"{user_id}_{job_id}_"
        return Path(tempfile.mkdtemp(prefix=prefix, dir=self.temp_root))

    def cleanup_job_dir(self, path: Path | None) -> None:
        cleanup_dir(path)
