from typing import Callable


def assert_not_none[T](val: T | None) -> T:
    if val is None:
        raise ValueError("Argument cannot be None")
    return val


def run_on_start(f: Callable):
    if not getattr(f, "__ran_on_start__", False):
        f()
        setattr(f, "__ran_on_start__", True)
    return f

