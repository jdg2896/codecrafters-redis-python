import time

from app.constants import NONE
from app.types import DataStore
from app.utils import to_resp_simple_string


def handle(args: list[bytes], data_store: DataStore) -> bytes:
    key = args[0]
    value = data_store.get(key)
    if value is not None and (value[1] is None or value[1] > time.time()):
        if isinstance(value[0], bytes):
            return to_resp_simple_string(b'string')
        elif isinstance(value[0], list) and value[0] and isinstance(value[0][0], tuple):
            return to_resp_simple_string(b'stream')
        elif isinstance(value[0], list):
            return to_resp_simple_string(b'list')
        elif isinstance(value[0], set):
            return to_resp_simple_string(b'set')
        elif isinstance(value[0], dict) and all(isinstance(v, float) for v in value[0].values()):
            return to_resp_simple_string(b'zset')
        elif isinstance(value[0], dict):
            return to_resp_simple_string(b'hash')
        elif isinstance(value[0], bytes) and value[0].startswith(b'\x00\x00\x00\x01'):
            return to_resp_simple_string(b'vectorset')
        else:
            return to_resp_simple_string(b'none')
    else:
        return to_resp_simple_string(b'none')