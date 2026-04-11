from app.types import DataStore
from app.utils import to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    if len(args) != 1:
        return b"-ERR wrong number of arguments for 'ECHO' command\r\n"
    return to_resp_bulk_string(args[0])