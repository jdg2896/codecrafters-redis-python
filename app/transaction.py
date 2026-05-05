from typing import Awaitable, Callable

from app.constants import NULL_ARRAY, OK, QUEUED
from app.types import DataStore
from app.utils import to_resp_array, to_resp_error

Dispatch = Callable[[bytes, list[bytes], DataStore], Awaitable[bytes]]


def new_connection_state() -> dict:
    return {"in_multi": False, "queue": [], "watched_keys": {}}


def reset(connection: dict) -> None:
    connection["in_multi"] = False
    connection["queue"] = []
    connection["watched_keys"] = {}


async def handle(
    command: bytes,
    args: list[bytes],
    connection: dict,
    data_store: DataStore,
    dispatch: Dispatch,
) -> bytes | None:
    """Handle MULTI/EXEC/DISCARD/WATCH/UNWATCH and queueing.

    Returns response bytes if the command was transaction-related (handled here),
    or None if the caller should dispatch the command normally.
    """
    cmd = command.upper()

    if cmd == b"MULTI":
        connection["in_multi"] = True
        connection["queue"] = []
        return OK

    if connection["in_multi"]:
        if cmd == b"EXEC":
            for key, snapshot in connection["watched_keys"].items():
                if data_store.get(key) != snapshot:
                    reset(connection)
                    return NULL_ARRAY
            queue = connection["queue"]
            reset(connection)
            results = []
            for queued_cmd, queued_args in queue:
                results.append(await dispatch(queued_cmd, queued_args, data_store))
            return to_resp_array(results)
        if cmd == b"DISCARD":
            reset(connection)
            return OK
        if cmd == b"WATCH":
            return to_resp_error(b"ERR WATCH inside MULTI is not allowed")
        connection["queue"].append((command, args))
        return QUEUED

    if cmd == b"EXEC":
        return to_resp_error(b"ERR EXEC without MULTI")
    if cmd == b"DISCARD":
        return to_resp_error(b"ERR DISCARD without MULTI")
    if cmd == b"WATCH":
        for key in args:
            connection["watched_keys"][key] = data_store.get(key)
        return OK
    if cmd == b"UNWATCH":
        connection["watched_keys"] = {}
        return OK

    return None
