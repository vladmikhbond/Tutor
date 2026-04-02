import json
import urllib.parse
from typing import Dict
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.models.pset_models import User, Ticket
from app.routers.login_router import get_current_tutor

from ..models.attend_models import Log
from ..dal import  get_users_db, get_attend_db #, get_pss_db
from ..routers.utils import time_to_str

router = APIRouter()

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")


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
    logs = db.query(Log).filter(Log.username == username).all()
    
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
    visits_list = [(fst, f"{snd // 60000}' {snd // 1000 % 60}\"") for fst, snd in visits_list] 

    last_visit = max(log.when for log in logs) 

    return templates.TemplateResponse(request, "stat/visits.html", {
            "student": username,
            "logs": visits_list, 
            "last_visit": time_to_str(last_visit, "%Y-%m-%d")})


# ----------------------- report
import re
from app.routers.user_router import USER_FILTER_KEY
from urllib.parse import unquote

@router.get("/report")
async def get_stat_report(
    request: Request, 
    users_db: Session = Depends(get_users_db),
    # pss_db: Session = Depends(get_pss_db),
    attend_db: Session = Depends(get_attend_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Звіт по відфільтрованим студентам.
    """  
    user_names = [username for (username,) in users_db.query(User.username).all()]
    filter_value = unquote(request.cookies.get(USER_FILTER_KEY, "")).strip()
    names = [n for n in user_names if re.search(filter_value, n, re.RegexFlag.U) is not None]
    
    # Перегляд конспектів
    logs = attend_db.query(Log).filter(Log.username.in_(names)).all()
    lec_dict = dict()
    for log in logs:
        obj = json.loads(log.body)
        duration = obj['duration']
        if log.username in lec_dict:
            lec_dict[log.username] += duration
        else:
            lec_dict[log.username] = duration

    return lec_dict 
    
    # # Вирішення задач
    # tickets = pss_db.query(Ticket.username, Ticket.state).filter(Ticket.username.in_(names)).all()
    # prob_dict = dict()
    # for username, state in tickets:
    #     if username in prob_dict:
    #         prob_dict[username] += state
    #     else:
    #         prob_dict[username] = state
    # return prob_dict

    # return templates.TemplateResponse(request, "user/list.html", 
    #         {"users": users, "filter_val": filter_value})
