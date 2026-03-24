from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.utils import utc_now


@dataclass(slots=True)
class UserSettings:
    user_id: int
    thumbnail_file_id: str | None = None
    caption_template: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    metadata_enabled: bool = False
    metadata_text: str = "IIUO Rename Bot"
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "UserSettings":
        return cls(
            user_id=document["_id"],
            thumbnail_file_id=document.get("thumbnail_file_id"),
            caption_template=document.get("caption_template"),
            prefix=document.get("prefix"),
            suffix=document.get("suffix"),
            metadata_enabled=bool(document.get("metadata_enabled", False)),
            metadata_text=document.get("metadata_text") or "IIUO Rename Bot",
            created_at=document.get("created_at") or utc_now(),
            updated_at=document.get("updated_at") or utc_now(),
        )

    def to_document(self) -> dict[str, Any]:
        return {
            "_id": self.user_id,
            "thumbnail_file_id": self.thumbnail_file_id,
            "caption_template": self.caption_template,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "metadata_enabled": self.metadata_enabled,
            "metadata_text": self.metadata_text,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
