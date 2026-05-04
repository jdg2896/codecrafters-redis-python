from app.constants import PONG
from app.types import DataStore


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    return PONG
