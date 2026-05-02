import asyncio
import time

from app.constants import NULL_ARRAY
from app.types import DataStore
from app.utils import to_resp_array, to_resp_bulk_string

POLL_INTERVAL = 0.1  # seconds between checks

async def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    timeout = float(args[1])
    deadline = time.time() + timeout if timeout > 0 else float('inf')

    while True:
        if key in data_store:
            list = data_store[key][0]
            if list:
                value = list.pop(0)
                return to_resp_array([to_resp_bulk_string(key), to_resp_bulk_string(value)])

        # If the key is not found or the list is empty, check if the timeout has been reached
        if time.time() >= deadline:
            return NULL_ARRAY

        await asyncio.sleep(POLL_INTERVAL)