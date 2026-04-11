from app.constants import NIL
from app.types import DataStore
from app.utils import to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    if key not in data_store:
        return NIL
    # Remove and return the first element from the list
    value = data_store[key][0].pop(0)
    print("LPOP result for key:", key, "Value:", value)
    return to_resp_bulk_string(value)