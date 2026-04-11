from app.constants import NIL
from app.types import DataStore
from app.utils import to_resp_array, to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    number = int(args[1]) if len(args) > 1 else 1
    if key not in data_store:
        return NIL

    list = data_store[key][0]
    if not list:
        return NIL

    count = min(number, len(list))
    values = [list.pop(0) for _ in range(count)]

    if len(values) == 1 and len(args) == 1:  # no count arg → return single bulk string
        return to_resp_bulk_string(values[0])
    return to_resp_array(values)