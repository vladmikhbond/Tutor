import json
import urllib.parse
from typing import Dict
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.models.pset_models import User
from app.routers.login_router import get_current_tutor

from ..models.attend_models import Log
from ..dal import get_attend_db
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
        return templates.TemplateResponse("stat/visits.html", {"request": request, "student": username, "logs": []})

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

    return templates.TemplateResponse("stat/visits.html", {"request": request, 
            "student": username,
            "logs": visits_list, 
            "last_visit": time_to_str(last_visit, "%Y-%m-%d")})

