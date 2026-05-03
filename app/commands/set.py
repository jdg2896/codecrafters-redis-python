from app.constants import OK
from app.types import DataStore
from app.utils import compute_expiry, to_resp_error


def handle(args: list[bytes], data_store: DataStore) -> bytes:
	key = args[0]
	value = args[1]
	expiry_unit = args[2] if len(args) > 2 else None
	expiry_value = int(args[3]) if len(args) > 3 else None

	# Handle optional expiry parameters
	try:
		expires_at = compute_expiry(expiry_unit, expiry_value)
	except ValueError as e:
		return to_resp_error(f"ERR {e}".encode())

	data_store[key] = (value, expires_at)

	return OK