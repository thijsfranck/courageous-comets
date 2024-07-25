import typing


def contextmenu(name: str) -> typing.Callable:
    """Mark a function as a context menu."""

    def wrap(func: typing.Callable) -> typing.Callable:
        func.is_contextmenu = True
        func.name = name
        return func

    return wrap
