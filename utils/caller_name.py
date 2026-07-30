import inspect


def get_caller_module_name() -> str | None:
    frame = inspect.currentframe()
    try:
        if frame is None or frame.f_back is None or frame.f_back.f_back is None:
            return None

        return frame.f_back.f_back.f_globals.get("__name__")
    finally:
        del frame
