from contextvars import ContextVar

_request_info: ContextVar[dict | None] = ContextVar("request_info", default=None)


def start_request_tracking() -> dict:
    info = {"cache": "-"}
    _request_info.set(info)
    return info


def mark_cache(status: str) -> None:
    info = _request_info.get()
    if info is not None:
        info["cache"] = status