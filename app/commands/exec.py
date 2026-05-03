from app.constants import OK
from app.types import DataStore
from app.utils import to_resp_error


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    return to_resp_error(b'ERR EXEC without MULTI')
    # return OK