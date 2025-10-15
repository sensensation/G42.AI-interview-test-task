import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from typer import Typer
import uvicorn

from app.configs.base import settings
from app.containers import Container

T = TypeVar("T")
P = ParamSpec("P")

app = Typer()


def coro[**P, T](func: Callable[P, Awaitable[T]]) -> Callable[P, T]:
    """Make it possible to run async code in sync context."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        async def async_wrapper(*args_: P.args, **kwargs_: P.kwargs) -> T:
            return await func(*args_, **kwargs_)

        return asyncio.get_event_loop().run_until_complete(async_wrapper(*args, **kwargs))

    return wrapper


@app.command()
def run_server() -> None:
    uvicorn_settings = settings.uvicorn
    uvicorn.run(**uvicorn_settings.dict())


@app.command(help="Description of custom command")
@coro
async def cli_example_command() -> None:
    # some code
    pass


if __name__ == "__main__":
    container = Container()
    container.wire(modules=[__name__])

    app()
