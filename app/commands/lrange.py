from app.constants import EMPTY_ARRAY
from app.types import DataStore
from app.utils import to_resp_array


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    start = int(args[1])
    stop = int(args[2])

    # If list is empty or key does not exist, return empty array
    if key not in data_store:
        return EMPTY_ARRAY
    
    # If start index is greater than or equal to the length of the list, return empty array
    if start >= len(data_store[key][0]):
        return EMPTY_ARRAY
    
    # If stop index is greater than or equal to the length of the list, adjust it to the last index
    if stop >= len(data_store[key][0]):
        stop = len(data_store[key][0]) - 1

    # If start index is greater than stop index, return empty array
    if start > stop:
        return EMPTY_ARRAY

    values = data_store[key][0]
    return to_resp_array(values[start:stop+1])