from app.types import DataStore
from app.utils import to_resp_simple_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    return to_resp_simple_string(
        b"FULLRESYNC 8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb 0"
    )
