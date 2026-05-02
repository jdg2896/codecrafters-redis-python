from app.constants import NONE
from app.types import DataStore
from app.utils import to_resp_array, to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    # args format: [b'streams', key1, key2, ..., id1, id2, ...]
    streams_args = args[1:]
    n = len(streams_args) // 2
    stream_keys = streams_args[:n]
    ids = streams_args[n:]

    result = []
    for stream_key, id in zip(stream_keys, ids):
        stream = data_store.get(stream_key, ([], None))[0]
        entries = [
            (entry_id, key_value_pairs) for entry_id, key_value_pairs in stream
            if tuple(map(int, entry_id.split(b'-'))) > tuple(map(int, id.split(b'-')))
        ]
        if entries:
            result.append(
                to_resp_array([
                    to_resp_bulk_string(stream_key),
                    to_resp_array([
                        to_resp_array([
                            to_resp_bulk_string(entry_id),
                            to_resp_array([to_resp_bulk_string(kv) for kv in key_value_pairs])
                        ]) for entry_id, key_value_pairs in entries
                    ])
                ])
            )

    return to_resp_array(result) if result else NONE