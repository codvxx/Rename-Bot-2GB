from __future__ import annotations

from pyrogram import filters


async def _is_admin(_, client, update) -> bool:
    user = getattr(update, "from_user", None)
    return bool(user and user.id in client.ctx.settings.admin_ids)


admin_filter = filters.create(_is_admin)
