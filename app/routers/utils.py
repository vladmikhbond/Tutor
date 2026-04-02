import re
from urllib.parse import unquote
from typing import List
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# -------------------- FILTERS

USER_FILTER_KEY = "tutor_user_filter"


def get_filtered_lines(lines: List[str], filter_key, request):
    """
    Повертає відфільтровані рядки.
    """
    filter = unquote(request.cookies.get(filter_key, ""))     
    if filter:
        lines = [line for line in lines if re.search(filter, line, re.RegexFlag.U) is not None] 
    return lines


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
