from __future__ import annotations

import logging
from functools import wraps


def safe_handler(logger: logging.Logger, user_message: str = "Request failed. Please try again."):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, update, *args, **kwargs):
            try:
                return await func(client, update, *args, **kwargs)
            except Exception:
                logger.exception("Unhandled handler error")
                message = getattr(update, "message", update)
                try:
                    if hasattr(update, "answer"):
                        try:
                            await update.answer("Action failed", show_alert=False)
                        except Exception:
                            pass
                    if hasattr(message, "reply_text"):
                        await message.reply_text(user_message)
                except Exception:
                    logger.exception("Failed to send fallback error message")

        return wrapper

    return decorator
