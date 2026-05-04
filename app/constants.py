# RESP protocol constants
CRLF = b"\r\n"

# Common RESP responses
PONG = b"+PONG" + CRLF
OK = b"+OK" + CRLF
NONE = b"+none" + CRLF
QUEUED = b"+QUEUED" + CRLF
NIL = b"$-1" + CRLF
EMPTY_ARRAY = b"*0" + CRLF
NULL_ARRAY = b"*-1" + CRLF
