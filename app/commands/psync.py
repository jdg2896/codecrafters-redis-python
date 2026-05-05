from pathlib import Path

from app.config import server_config
from app.constants import CRLF
from app.types import DataStore
from app.utils import to_resp_simple_string

EMPTY_RDB = (Path(__file__).parent.parent / "data" / "empty.rdb").read_bytes()


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    repl_id = server_config["master_replid"]
    fullresync = to_resp_simple_string(f"FULLRESYNC {repl_id} 0".encode())
    rdb_payload = b"$" + str(len(EMPTY_RDB)).encode() + CRLF + EMPTY_RDB
    return fullresync + rdb_payload
