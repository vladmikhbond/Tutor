from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# # str(Kyiv) -> time(UTC)
# def str_to_time(s: str, TIME_FMT) -> datetime:
#     return datetime.strptime(s, TIME_FMT) \
#         .replace(tzinfo=ZoneInfo("Europe/Kyiv")) \
#         .astimezone(ZoneInfo("UTC")) \
#         .replace(tzinfo=None)

# # time(UTC) -> str(Kyiv)

#--------------------------------- time(UTC) <--> str(Kyiv) ------------------------  

FMT = "%Y-%m-%dT%H:%M"
ZONE = "Europe/Kyiv"

def time_to_str(dt: datetime, fmt = FMT) -> str:
    return dt.astimezone(ZoneInfo(ZONE)).strftime(fmt)

def str_to_time(s: str, fmt = FMT) -> datetime:
    return datetime.strptime(s, fmt) \
        .replace(tzinfo=ZoneInfo(ZONE)) \
        .astimezone(ZoneInfo("UTC")) \
        .replace(tzinfo=None)

def delta_to_str(td):
    return f"{td.days} d {td.seconds//3600} h {(td.seconds//60)%60} m"
