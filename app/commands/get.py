import time

from app.constants import NIL
from app.types import DataStore
from app.utils import to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    value = data_store.get(key)
    if value is not None and (value[1] is None or value[1] > time.time()):
        # If value is not bytes, convert it to string and then to bytes
        data = value[0] if isinstance(value[0], bytes) else str(value[0]).encode()
        return to_resp_bulk_string(data)
    else:
        return NIL
