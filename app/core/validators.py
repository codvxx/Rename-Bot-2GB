from __future__ import annotations

import os
import re
import string
from pathlib import Path

from app.core.exceptions import ConfigError, ValidationError

TRUE_VALUES = {"1", "true", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "no", "n", "off"}
INVALID_FILENAME_CHARS = r'<>:"/\\|?*'
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
ALLOWED_CAPTION_FIELDS = {"filename", "filesize", "duration"}


def parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ConfigError(f"Invalid boolean value: {value!r}")


def parse_int(value: str | None, name: str) -> int:
    if value is None or not value.strip():
        raise ConfigError(f"Missing required environment variable: {name}")
    try:
        return int(value.strip())
    except ValueError as exc:
        raise ConfigError(f"Environment variable {name} must be an integer") from exc


def parse_positive_int(value: str | None, name: str, *, default: int) -> int:
    if value is None or not value.strip():
        return default
    parsed = parse_int(value, name)
    if parsed <= 0:
        raise ConfigError(f"Environment variable {name} must be greater than 0")
    return parsed


def parse_admin_ids(value: str | None) -> tuple[int, ...]:
    if value is None or not value.strip():
        raise ConfigError("Missing required environment variable: ADMIN_IDS")
    tokens = [token.strip() for token in re.split(r"[,\s]+", value) if token.strip()]
    if not tokens:
        raise ConfigError("ADMIN_IDS must contain at least one Telegram user ID")
    try:
        return tuple(sorted({int(token) for token in tokens}))
    except ValueError as exc:
        raise ConfigError("ADMIN_IDS must contain only integers") from exc


def parse_force_subs(value: str | None) -> tuple[str, ...]:
    if value is None or not value.strip():
        return ()
    items = []
    for token in re.split(r"[,\s]+", value.strip()):
        cleaned = token.strip().lstrip("@")
        if not cleaned:
            continue
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", cleaned):
            raise ConfigError("FORCE_SUBS contains an invalid channel username or chat ID")
        items.append(cleaned)
    return tuple(dict.fromkeys(items))


def require_env(value: str | None, name: str) -> str:
    if value is None or not value.strip():
        raise ConfigError(f"Missing required environment variable: {name}")
    return value.strip()


def sanitize_filename(name: str, *, default_extension: str = "") -> str:
    if not isinstance(name, str):
        raise ValidationError("Filename must be text")
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", " ", name)
    cleaned = cleaned.replace("/", " ").replace("\\", " ")
    cleaned = cleaned.replace("..", " ")
    cleaned = cleaned.strip().strip(".")
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        raise ValidationError("Filename cannot be empty")

    path = Path(cleaned)
    suffix = path.suffix[:16]
    stem = path.stem if suffix else cleaned
    translation = str.maketrans({char: " " for char in INVALID_FILENAME_CHARS})
    stem = stem.translate(translation)
    stem = re.sub(r"\s+", " ", stem).strip(" ._")
    suffix = suffix.translate(translation).strip().replace(" ", "")

    if not stem:
        stem = "file"

    if stem.upper() in WINDOWS_RESERVED_NAMES:
        stem = f"{stem}_file"

    effective_suffix = suffix or default_extension
    if effective_suffix and not effective_suffix.startswith("."):
        effective_suffix = f".{effective_suffix}"

    max_stem_length = 180 - len(effective_suffix)
    stem = stem[: max(1, max_stem_length)].rstrip(" ._")
    if not stem:
        stem = "file"

    result = f"{stem}{effective_suffix}"
    if result in {".", ".."}:
        raise ValidationError("Filename is invalid")
    return result


def sanitize_affix(value: str, *, field_name: str) -> str:
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", " ", value or "")
    cleaned = cleaned.replace("/", " ").replace("\\", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        raise ValidationError(f"{field_name} cannot be empty")
    return cleaned[:64]


def sanitize_metadata_text(value: str) -> str:
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", " ", value or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        raise ValidationError("Metadata text cannot be empty")
    return cleaned[:128]


def validate_caption_template(template: str) -> str:
    if not template or not template.strip():
        raise ValidationError("Caption template cannot be empty")
    if len(template) > 1024:
        raise ValidationError("Caption template is too long")

    formatter = string.Formatter()
    for _, field_name, _, _ in formatter.parse(template):
        if field_name and field_name not in ALLOWED_CAPTION_FIELDS:
            allowed = ", ".join(sorted(ALLOWED_CAPTION_FIELDS))
            raise ValidationError(f"Unsupported placeholder: {field_name}. Allowed: {allowed}")
    return template.strip()


def validate_file_size(file_size: int | None, max_bytes: int) -> None:
    if file_size is None:
        return
    if file_size > max_bytes:
        max_mb = max_bytes // (1024 * 1024)
        raise ValidationError(f"This file exceeds the configured size limit of {max_mb} MB")


def ensure_directory(path: str) -> str:
    normalized = os.path.abspath(path)
    os.makedirs(normalized, exist_ok=True)
    return normalized
