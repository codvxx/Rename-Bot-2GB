from __future__ import annotations

from aiohttp import web

from app.web.health import health_handler, root_handler


def create_web_app(settings) -> web.Application:
    app = web.Application()
    app["settings"] = settings
    app.router.add_get("/", root_handler)
    app.router.add_get("/health", health_handler)
    return app
