from app.types import DataStore
from app.utils import to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
	stream_key = args[0]
	entry_id = args[1]
	key_value_pairs = args[2:]

	existing = data_store.get(stream_key)
	stream = existing[0] if existing is not None else []
	stream.append((entry_id, key_value_pairs))
	data_store[stream_key] = (stream, None)

	return to_resp_bulk_string(entry_id)