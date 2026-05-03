from app.types import DataStore
from app.utils import to_resp_bulk_string, to_resp_error


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    if len(args) != 1:
        return to_resp_error(b"ERR wrong number of arguments for 'ECHO' command")
    return to_resp_bulk_string(args[0])