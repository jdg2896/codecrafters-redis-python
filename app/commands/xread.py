from app.constants import NONE
from app.types import DataStore
from app.utils import to_resp_array, to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    # args format: [b'streams', stream_key, id]
    stream_key = args[1]
    id = args[2]
    stream = data_store.get(stream_key, ([], None))[0]

    # Return the entries with IDs greater than the specified ID. The ID is a string in the format <millisecondsTime>-<sequenceNumber>.
    entries = [
        (entry_id, key_value_pairs) for entry_id, key_value_pairs in stream
        if tuple(map(int, entry_id.split(b'-'))) > tuple(map(int, id.split(b'-')))
    ]
    if not entries:
        return NONE
    return to_resp_array([
        to_resp_array([
            to_resp_bulk_string(stream_key),
            to_resp_array([
                to_resp_array([
                    to_resp_bulk_string(entry_id),
                    to_resp_array([to_resp_bulk_string(kv) for kv in key_value_pairs])
                ]) for entry_id, key_value_pairs in entries
            ])
        ])
    ])