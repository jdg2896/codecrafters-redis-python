from app.types import DataStore
from app.utils import to_resp_array, to_resp_error


def handle(args: list[bytes], data_store: DataStore, connection: dict) -> bytes:
    in_multi = connection.get("in_multi")
    queue = connection.get("queue", [])
    print("In EXEC handler, in_multi:", in_multi, "queue:", queue)
    if in_multi:
        connection["in_multi"] = False
        connection["queue"] = []
    else: 
        return to_resp_error(b"ERR EXEC without MULTI")
    return to_resp_array(queue)