from typing import Any

DataStore = dict[bytes, tuple[Any, float | None]]  # key -> (value, expires_at)
