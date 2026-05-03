from app.types import DataStore
from app.utils import to_resp_integer


async def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    # Get the current value, defaulting to 0 if the key doesn't exist or has expired
    value = int(data_store.get(key, (0, None))[0])
    value += 1
    data_store[key] = (value, None)
    return to_resp_integer(value)
