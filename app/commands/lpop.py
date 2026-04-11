from app.constants import NIL
from app.types import DataStore
from app.utils import to_resp_array, to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    number = int(args[1]) if len(args) > 1 else 1
    if key not in data_store:
        return NIL
    # Remove and return the first element from the list
    list = data_store[key][0]
    values = list[:number]
    if not list:
        return NIL
    for _ in range(number):
        values = list.pop(0)
    
    print("LPOP result for key:", key, "Value:", values)
    if len(values) == 1:
        return to_resp_bulk_string(values[0])
    elif len(values) > 1:
        return to_resp_array(values)
    else:
        return NIL