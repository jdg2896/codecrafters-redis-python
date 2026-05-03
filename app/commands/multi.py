from app.constants import OK
from app.types import DataStore


def handle(args: list[bytes], data_store: DataStore, connection: dict) -> bytes:
    connection["in_multi"] = True
    connection["queue"] = []
    return OK