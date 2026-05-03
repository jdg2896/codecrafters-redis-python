from app.constants import OK
from app.types import DataStore
from app.utils import to_resp_bulk_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    return OK