import asyncio
import time

from app.constants import CRLF


__all__ = [
    "compute_expiry",
    "get_client_address",
    "to_resp_bulk_string",
    "to_resp_simple_string",
    "to_resp_integer",
    "to_resp_array",
]


# Utility functions
def compute_expiry(expiry_unit: bytes | None, expiry_value: int | None) -> float | None:
    '''Returns the expiry time for a key in the data store. 
    
    The expiry time can be specified in milliseconds (PX) or seconds (EX).'''
    if not expiry_unit or not expiry_value:
        return None

    try:
        ms = int(expiry_value)
    except ValueError:
        raise ValueError(f"invalid expiry time: {expiry_value!r}")
    
    if expiry_unit.upper() == b'PX':
        return time.time() + ms / 1000
    elif expiry_unit.upper() == b'EX':
        return time.time() + ms
    else:
        raise ValueError(f"unknown expiry unit: {expiry_unit!r}")


def get_client_address(writer: asyncio.StreamWriter):
    return writer.get_extra_info("peername")


def to_resp_bulk_string(data: bytes):
    return b"$" + str(len(data)).encode() + CRLF + data + CRLF


def to_resp_simple_string(data: bytes):
    return b"+" + data + CRLF


def to_resp_integer(value: int):
    return b":" + str(value).encode() + CRLF


def to_resp_array(items: list[bytes]):
    resp = b"*" + str(len(items)).encode() + CRLF
    for item in items:
        resp += to_resp_bulk_string(item)
    return resp