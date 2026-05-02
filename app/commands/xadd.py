from app.types import DataStore
from app.utils import to_resp_bulk_string, to_resp_error

ENTRY_ID_NOT_ZERO_ERROR = b"ERR The ID specified in XADD must be greater than 0-0"
ENTRY_ID_EQUAL_OR_SMALLER_ERROR = b"ERR The ID specified in XADD is equal or smaller than the target stream top item"


def handle(args: list[bytes], data_store: DataStore) -> bytes:
	stream_key = args[0]
	entry_id = args[1]
	key_value_pairs = args[2:]

	if entry_id == b"0-0":
		return to_resp_error(ENTRY_ID_NOT_ZERO_ERROR)

	# Validate that the entry id:
	# - is in the format of <millisecondsTime>-<sequenceNumber>
	# - millisecondsTime is a valid integer
	# - sequenceNumber is a valid integer
	# - millisecondsTime must be greater than or equal to the last entry's millisecondsTime
	# - if the millisecondsTime values are equal, the sequenceNumber of the new ID must be greater than the last entry's sequenceNumber
	for entry in data_store.get(stream_key, ([], None))[0]:
		last_entry_id = entry[0]
		last_milliseconds_time, last_sequence_number = map(int, last_entry_id.split(b'-'))
		new_milliseconds_time, new_sequence_number = map(int, entry_id.split(b'-'))

		if new_milliseconds_time < last_milliseconds_time:
			return to_resp_error(ENTRY_ID_EQUAL_OR_SMALLER_ERROR)
		elif (
				new_milliseconds_time == last_milliseconds_time
				and new_sequence_number <= last_sequence_number
		):
			return to_resp_error(ENTRY_ID_EQUAL_OR_SMALLER_ERROR)

	existing = data_store.get(stream_key)
	stream = existing[0] if existing is not None else []
	stream.append((entry_id, key_value_pairs))
	data_store[stream_key] = (stream, None)

	return to_resp_bulk_string(entry_id)