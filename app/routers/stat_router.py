import os, json
import urllib.parse
from typing import Dict
from fastapi import Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pset_models import User, Ticket
from app.routers.login_router import get_current_tutor

from ..models.attend_models import Log
from ..dal import  get_users_db, get_attend_db, get_pss_db
from ..routers.utils import time_to_str

import re
from app.routers.utils import USER_FILTER_KEY
from urllib.parse import unquote


router = APIRouter()

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

DURO_URL = os.getenv("DURO_URL")

# -------------------------- visits -------------------------

@router.get("/visits/{username}")
async def get_stat_visits(
    username: str,
    request: Request, 
    db: Session = Depends(get_attend_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Перегляд лекцій студентом
    log.body = {lecture: ... , duration: ... }
    """
    logs = db.execute(select(Log).where(Log.username == username)).scalars().all()
    
    if len(logs) == 0:
        return templates.TemplateResponse(request, "stat/visits.html", {"student": username, "logs": []})

    visits_dict: Dict[str, int] = {}
    

    for log in logs:
        obj = json.loads(log.body)
        lecture = urllib.parse.unquote(obj['lecture'])    
        duration = obj['duration']
        if lecture in visits_dict:
            visits_dict[lecture] += duration
        else: 
            visits_dict[lecture] = duration
        
    visits_list = sorted( visits_dict.items(), key=lambda x: x[0])
    visits_list = [(lec, f"{msec // 60000}' {msec // 1000 % 60}\"") for lec, msec in visits_list] 

    last_visit = max(log.when for log in logs) 

    return templates.TemplateResponse(request, "stat/visits.html", {
            "student": username,
            "logs": visits_list, 
            "last_visit": time_to_str(last_visit, "%Y-%m-%d")})


# ----------------------- report


@router.get("/report")
async def get_stat_report(
    request: Request, 
    users_db: Session = Depends(get_users_db),
    pss_db: Session = Depends(get_pss_db),
    attend_db: Session = Depends(get_attend_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Звіт по відфільтрованим студентам.
    """  
    user_names = [username for (username,) in users_db.execute(select(User.username)).all()]
    filter_value = unquote(request.cookies.get(USER_FILTER_KEY, "")).strip()
    names = [n for n in user_names if re.search(filter_value, n, re.RegexFlag.U) is not None]
    names.sort()
    err_mes = ""

    # Перегляд конспектів
    logs = attend_db.execute(select(Log).where(Log.username.in_(names))).scalars().all()
    lect_dict = dict()
    for log in logs:
        obj = json.loads(log.body)
        duration = obj['duration']
        if log.username in lect_dict:
            lect_dict[log.username] += duration
        else:
            lect_dict[log.username] = duration
    for k in lect_dict:
        msec = lect_dict[k]
        lect_dict[k] = f"{msec // 60000}' {msec // 1000 % 60}\""
    
    # Вирішення задач
    tickets = pss_db.execute(select(Ticket.username, Ticket.state).where(Ticket.username.in_(names))).all()
    prob_dict = dict()
    for username, state in tickets:
        if username in prob_dict:
            prob_dict[username] += state
        else:
            prob_dict[username] = state

    # Виконання тестів
    try:
        test_dict = await fetch_tests(filter_value)
        for name in test_dict:
            scores = test_dict[name]
            avg = round(sum(scores) / len(scores)) if scores else 0
            test_dict[name] = f"{avg}%  ({len(scores)})" if len(scores) else ""
    except Exception as e:
        test_dict = []
        err_mes = str(e)

    return templates.TemplateResponse(request, "stat/report.html", {
        "names": names, "err_mes": err_mes,
        "lect_dict": lect_dict, "prob_dict": prob_dict, "test_dict": test_dict})




async def fetch_tests(pattern: str):
    """
        {"cAlieksieiev": [100, 57, 75], ... }
    """
    URL = f"{DURO_URL}/ticket/remote"

    async with httpx.AsyncClient() as client:
        try:
            client_response = await client.post(
                URL,
                json={"pattern": pattern},
            )
        except httpx.RequestError as e:
            raise Exception(f"Cannot get an answer from '{URL}': {e}") from e

    if client_response.is_success:
        return client_response.json()
    else:
        raise Exception(f"Wrong response. Status code: {client_response.status_code}")
