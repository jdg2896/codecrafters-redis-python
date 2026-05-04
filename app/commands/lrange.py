from app.constants import EMPTY_ARRAY
from app.types import DataStore
from app.utils import to_resp_array, to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    start = int(args[1])
    stop = int(args[2])
    list = data_store[key][0] if key in data_store else []
    list_length = len(list)
    print(
        "Handling LRANGE command for key:",
        key,
        "Start:",
        start,
        "Stop:",
        stop,
        "List length:",
        list_length,
        "List:",
        list,
    )

    # Handle negative indices, converting them to positive indices
    if start < 0:
        start += list_length
        # If still out of bounds after adjustment, clamp to 0
        if start < 0:
            start = 0

    if stop < 0:
        stop += list_length
        # If still out of bounds after adjustment, clamp to 0
        if stop < 0:
            stop = 0

    # If list is empty or key does not exist, return empty array
    if key not in data_store:
        return EMPTY_ARRAY

    # If start index is out of bounds, return empty array
    if start >= list_length:
        return EMPTY_ARRAY

    # If stop index is out of bounds, clamp to last index
    if stop >= list_length:
        stop = list_length - 1

    # If start index is greater than stop index, return empty array
    if start > stop:
        return EMPTY_ARRAY

    values = data_store[key][0]
    print("LRANGE result for key:", key, "Values:", values[start : stop + 1])
    return to_resp_array([to_resp_bulk_string(v) for v in values[start : stop + 1]])
