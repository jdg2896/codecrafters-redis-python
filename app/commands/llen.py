from app.types import DataStore
from app.utils import to_resp_integer


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    list = data_store[key][0] if key in data_store else []
    list_length = len(list)

    print("LLEN result for key:", key, "Length:", list_length)
    return to_resp_integer(list_length)
