from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# str(Kyiv) -> time(UTC)
def str_to_time(s: str, TIME_FMT) -> datetime:
    return datetime.strptime(s, TIME_FMT) \
        .replace(tzinfo=ZoneInfo("Europe/Kyiv")) \
        .astimezone(ZoneInfo("UTC")) \
        .replace(tzinfo=None)