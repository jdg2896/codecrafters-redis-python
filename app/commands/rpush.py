from app.types import DataStore
from app.utils import to_resp_integer


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    values = args[1:]
    if key not in data_store:
        data_store[key] = ([], None)
    data_store[key][0].extend(values)
    return to_resp_integer(len(data_store[key][0]))