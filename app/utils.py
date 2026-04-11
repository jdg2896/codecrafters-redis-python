import asyncio
import time

from .constants import CRLF

__all__ = ["compute_expiry", "get_client_address", "to_resp_bulk_string", "to_resp_integer"]

# Utility functions
def compute_expiry(expiry_unit: bytes | None, expiry_value: int | None):
    '''Returns the expiry time for a key in the data store. 
    
    The expiry time can be specified in milliseconds (PX) or seconds (EX).'''
    try:
        expires_at = None
        if expiry_unit and expiry_value:
            ms = int(expiry_value)
            if expiry_unit == b'PX':
                expires_at = time.time() + ms / 1000
            elif expiry_unit == b'EX':
                expires_at = time.time() + ms
        
        return expires_at
    except ValueError:
        return b"-ERR invalid expiry time\r\n"


def get_client_address(writer: asyncio.StreamWriter):
    return writer.get_extra_info("peername")


def to_resp_bulk_string(data: bytes):
    return b"$" + str(len(data)).encode() + CRLF + data + CRLF


def to_resp_integer(value: int):
    return b":" + str(value).encode() + CRLF