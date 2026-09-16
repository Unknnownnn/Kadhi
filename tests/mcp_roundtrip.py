from __future__ import annotations

from contextlib import asynccontextmanager

import anyio


@asynccontextmanager
async def connected_session(server, *, raise_exceptions: bool = False):
    from mcp.client.session import ClientSession
    from mcp.shared.memory import create_client_server_memory_streams

    async with create_client_server_memory_streams() as (client_streams, server_streams):
        client_read, client_write = client_streams
        server_read, server_write = server_streams

        async with anyio.create_task_group() as task_group:
            task_group.start_soon(
                lambda: server.run(
                    server_read,
                    server_write,
                    server.create_initialization_options(),
                    raise_exceptions=raise_exceptions,
                )
            )
            try:
                async with ClientSession(client_read, client_write) as session:
                    await session.initialize()
                    yield session
            finally:
                task_group.cancel_scope.cancel()


def is_error(result) -> bool:
    for attribute in ("isError", "is_error"):
        if hasattr(result, attribute):
            return bool(getattr(result, attribute))
    raise AttributeError(
        f"{type(result).__name__} exposes neither isError nor is_error; "
        "the mcp SDK renamed the field again (#322)"
    )


def input_schema(tool) -> dict:
    """Read an advertised ``Tool``'s schema on either mcp major (#322).

    Same rename as :func:`is_error`: the wire name is ``inputSchema`` and 2.x
    exposes it as ``input_schema``. Raises rather than returning ``{}`` for the
    same reason -- an empty schema would read as "the tool advertises nothing"
    instead of "the field moved".
    """
    for attribute in ("inputSchema", "input_schema"):
        if hasattr(tool, attribute):
            return getattr(tool, attribute)
    raise AttributeError(
        f"{type(tool).__name__} exposes neither inputSchema nor input_schema; "
        "the mcp SDK renamed the field again (#322)"
    )
