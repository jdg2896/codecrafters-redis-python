from app.types import DataStore
from app.utils import to_resp_integer


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    values = args[1:]
    if key not in data_store:
        data_store[key] = ([], None)
    # Prepend values to the list
    data_store[key][0][:0] = list(reversed(values))
    print("LPUSH result for key:", key, "Values:", data_store[key][0])
    return to_resp_integer(len(data_store[key][0]))
