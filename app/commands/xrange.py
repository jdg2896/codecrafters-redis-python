from app.constants import NONE
from app.types import DataStore
from app.utils import to_resp_array, to_resp_bulk_string

MAXIMUM_SEQUENCE_NUMBER = 2**64 - 1 # 18446744073709551615


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    stream_key = args[0]
    start = args[1]
    end = args[2]
    stream = data_store.get(stream_key, ([], None))[0]

    if start == b"-":
        start = b"0-0"

    start_milliseconds_time, start_sequence_number = map(int, start.split(b'-'))
    end_milliseconds_time, end_sequence_number = map(int, end.split(b'-'))

    # Sequence numbers are optional, and default to 0 for the start ID and to 18446744073709551615 for the end ID.
    if start_sequence_number is None:
        start_sequence_number = 0
    if end_sequence_number is None:
        end_sequence_number = MAXIMUM_SEQUENCE_NUMBER

    start_id = (start_milliseconds_time, start_sequence_number)
    end_id = (end_milliseconds_time, end_sequence_number)

    return to_resp_array([
        to_resp_array([
            to_resp_bulk_string(entry_id),
            to_resp_array([to_resp_bulk_string(kv) for kv in key_value_pairs])
        ]) for entry_id, key_value_pairs in stream
        if start_id <= tuple(map(int, entry_id.split(b'-'))) <= end_id
    ]) if stream else NONE