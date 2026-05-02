import asyncio
import time

from app.constants import NONE, NULL_ARRAY
from app.types import DataStore
from app.utils import to_resp_array, to_resp_bulk_string

POLL_INTERVAL = 0.01  # seconds


async def handle(args: list[bytes], data_store: DataStore) -> bytes:
    block_timeout_ms = None
    if args[0].upper() == b'BLOCK':
        block_timeout_ms = int(args[1])
        args = args[2:]

    # args format: [b'streams', key1, key2, ..., id1, id2, ...]
    streams_args = args[1:]
    n = len(streams_args) // 2
    stream_keys = streams_args[:n]
    ids = streams_args[n:]

    if block_timeout_ms is not None:
        deadline = time.time() + block_timeout_ms / 1000 if block_timeout_ms > 0 else float('inf')
        while True:
            result = _get_entries(stream_keys, ids, data_store)
            if result:
                return to_resp_array(result)
            if time.time() >= deadline:
                return NULL_ARRAY
            await asyncio.sleep(POLL_INTERVAL)

    result = _get_entries(stream_keys, ids, data_store)
    return to_resp_array(result) if result else NONE


def _get_entries(stream_keys, ids, data_store):
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
    return result