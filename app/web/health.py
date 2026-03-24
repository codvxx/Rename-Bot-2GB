from __future__ import annotations

from aiohttp import web


async def health_handler(request: web.Request) -> web.Response:
    settings = request.app["settings"]
    return web.json_response({"status": "ok", "app": settings.app_name})


async def root_handler(request: web.Request) -> web.Response:
    settings = request.app["settings"]
    return web.json_response({"message": f"{settings.app_name} is running"})
