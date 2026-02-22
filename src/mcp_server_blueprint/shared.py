"""Shared decorator for MCP handler error handling."""

import functools
import inspect
import json
from collections.abc import Awaitable, Callable


def handle_errors[**P](func: Callable[P, Awaitable[str]]) -> Callable[P, Awaitable[str]]:
    """Catch unhandled exceptions and return a structured JSON error response.

    When the handler has a `ctx` parameter, errors are also logged via ctx.error.
    Exceptions with a `status_code` attribute (e.g. ApiClientError) include it
    in the response; all others use status_code: null.
    """
    sig = inspect.signature(func)

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
        ctx = sig.bind_partial(*args, **kwargs).arguments.get("ctx")

        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if ctx is not None:
                await ctx.error(str(e))
            return json.dumps({"error": str(e), "status_code": getattr(e, "status_code", None)})

    return wrapper
