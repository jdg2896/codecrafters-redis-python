from app.constants import OK
from app.types import DataStore
from app.utils import to_resp_bulk_string
from app.config import server_config


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    args[0] = args[0].lower()  # subcommand is case-insensitive
    if args[0] == b"replication":
        role = server_config['role']
        replica_of = server_config['replica_of']
        replication_info = f"# Replication\r\nrole:{role}\r\nreplica_of:{replica_of}\r\n"
        return to_resp_bulk_string(replication_info.encode())
    else:
        return OK
