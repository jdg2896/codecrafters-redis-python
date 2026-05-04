from app.types import DataStore
from app.utils import to_resp_error, to_resp_integer

NOT_AN_INTEGER_ERROR = b"ERR value is not an integer or out of range"


async def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    # Get the current value, defaulting to 0 if the key doesn't exist or has expired
    value = data_store.get(key, (0, None))[0]

    if isinstance(value, bytes):
        try:
            value = int(value)
        except ValueError:
            return to_resp_error(NOT_AN_INTEGER_ERROR)
    elif not isinstance(value, int):
        return to_resp_error(NOT_AN_INTEGER_ERROR)

    value += 1
    data_store[key] = (value, None)
    return to_resp_integer(value)
