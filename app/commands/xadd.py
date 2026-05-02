from app.types import DataStore
from app.utils import to_resp_bulk_string, to_resp_error

ENTRY_ID_NOT_ZERO_ERROR = b"ERR The ID specified in XADD must be greater than 0-0"
ENTRY_ID_EQUAL_OR_SMALLER_ERROR = b"ERR The ID specified in XADD is equal or smaller than the target stream top item"


def handle(args: list[bytes], data_store: DataStore) -> bytes:
	stream_key = args[0]
	entry_id = args[1]
	key_value_pairs = args[2:]
	stream = data_store.get(stream_key, ([], None))[0]

	if entry_id == b"0-0":
		return to_resp_error(ENTRY_ID_NOT_ZERO_ERROR)
	
	# The entry ID can be specified as either a specific ID in the format of <millisecondsTime>-<sequenceNumber> or as an auto-generated ID using the special ID of '*'.
	new_milliseconds_time, new_sequence_number = (
		int(x) if x != b'*' else '*' for x in entry_id.split(b'-')
	)
	if new_sequence_number == '*':
		new_sequence_number = autogenerate_sequence_number(
			stream,
			int(new_milliseconds_time)
		)
		entry_id = f"{new_milliseconds_time}-{new_sequence_number}".encode()

	# Validate that the entry id:
	# - is in the format of <millisecondsTime>-<sequenceNumber>
	# - millisecondsTime is a valid integer
	# - sequenceNumber is a valid integer
	# - millisecondsTime must be greater than or equal to the last entry's millisecondsTime
	# - if the millisecondsTime values are equal, the sequenceNumber of the new ID must be greater than the last entry's sequenceNumber
	for entry in stream:
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


def autogenerate_sequence_number(stream: list[tuple[bytes, list[bytes]]], milliseconds_time: int) -> int:
	'''
	Autogenerates a sequence number for a new stream entry based on the existing entries in the stream.
	- If the stream is empty for a given time part, the sequence number starts at 0.
	- If there are already entries with the same time part, the new sequence number is the last sequence number + 1.
	- The only exception is when the time part is 0. In that case, the default sequence number starts at 1.
	'''
	if not stream:
		return 1 if milliseconds_time == 0 else 0
	last_entry_id = stream[-1][0]
	last_milliseconds_time, last_sequence_number = map(int, last_entry_id.split(b'-'))
	if milliseconds_time == last_milliseconds_time:
		return last_sequence_number + 1
	return 0