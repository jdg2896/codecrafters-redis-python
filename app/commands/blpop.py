import asyncio
import time

from app.constants import NIL
from app.types import DataStore
from app.utils import to_resp_array

POLL_INTERVAL = 0.1  # seconds between checks

async def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    timeout = float(args[1])  # last arg is always timeout
    deadline = time.time() + timeout if timeout > 0 else float('inf')

    while True:
        if key in data_store:
            list = data_store[key][0]
            if list:
                value = list.pop(0)
                return to_resp_array([key, value])

        if time.time() >= deadline:
            return NIL

        await asyncio.sleep(POLL_INTERVAL)