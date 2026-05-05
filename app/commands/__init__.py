from app.commands import (
    blpop,
    echo,
    get,
    incr,
    info,
    llen,
    lpop,
    lpush,
    lrange,
    ping,
    psync,
    replconf,
    rpush,
    set,
    xadd,
    xrange,
    xread,
)
from app.commands import (
    type as type_command,  # type is a reserved keyword, so we import it as type_command
)

# Command handlers mapping command names to their respective handler functions.
# Transaction commands (MULTI/EXEC/DISCARD/WATCH/UNWATCH) live in app/transaction.py.
COMMAND_HANDLERS = {
    b"PING": ping.handle,
    b"ECHO": echo.handle,
    b"SET": set.handle,
    b"GET": get.handle,
    b"RPUSH": rpush.handle,
    b"LRANGE": lrange.handle,
    b"LPUSH": lpush.handle,
    b"LLEN": llen.handle,
    b"LPOP": lpop.handle,
    b"BLPOP": blpop.handle,
    b"TYPE": type_command.handle,
    b"XADD": xadd.handle,
    b"XRANGE": xrange.handle,
    b"XREAD": xread.handle,
    b"INCR": incr.handle,
    b"INFO": info.handle,
    b"REPLCONF": replconf.handle,
    b"PSYNC": psync.handle,
}
