from app.commands import (
    blpop,
    llen,
    lpop,
    lpush,
    ping,
    echo,
    set,
    get,
    rpush,
    lrange,
    type as type_command, # type is a reserved keyword, so we import it as type_command
    xadd,
    xrange,
    xread,
    incr,
    info,
)

# Command handlers mapping command names to their respective handler functions.
# MULTI and EXEC are intentionally excluded — they are handled at the connection layer in main.py.
COMMAND_HANDLERS = {
    b'PING': ping.handle,
    b'ECHO': echo.handle,
    b'SET': set.handle,
    b'GET': get.handle,
    b'RPUSH': rpush.handle,
    b'LRANGE': lrange.handle,
    b'LPUSH': lpush.handle,
    b'LLEN': llen.handle,
    b'LPOP': lpop.handle,
    b'BLPOP': blpop.handle,
    b'TYPE': type_command.handle,
    b'XADD': xadd.handle,
    b'XRANGE': xrange.handle,
    b'XREAD': xread.handle,
    b'INCR': incr.handle,
    b'INFO': info.handle,
}