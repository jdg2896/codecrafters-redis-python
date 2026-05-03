import asyncio

from app.types import DataStore
from app.utils import to_resp_array, to_resp_error


async def handle(args: list[bytes], data_store: DataStore, connection: dict, command_handlers: dict) -> bytes:
    in_multi = connection.get("in_multi")
    queue = connection.get("queue", [])
    print("In EXEC handler, in_multi:", in_multi, "queue:", queue)
    if in_multi:
        connection["in_multi"] = False
        results = []
        for queued_cmd, queued_args in connection["queue"]:
            handler = command_handlers.get(queued_cmd.upper())
            if handler:
                res = handler(queued_args, data_store)
                if asyncio.iscoroutine(res):
                    res = await res
                results.append(res)
            else:
                results.append(to_resp_error(b"ERR unknown command"))
        connection["queue"] = []
        return to_resp_array(results)
    else: 
        return to_resp_error(b"ERR EXEC without MULTI")
