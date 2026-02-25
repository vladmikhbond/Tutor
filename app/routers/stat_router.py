from datetime import datetime
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.models.attend_report import create_matrix
from app.models.pset_models import User
from app.routers.login_router import get_current_tutor

from ..models.attend_models import Log, Shadule, Snapshot
from ..dal import get_attend_db

router = APIRouter()

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

import json
# -------------------------- visits -------------------------

@router.get("/visits/{username}")
async def get_stat_visits(
    username: str,
    request: Request, 
    db: Session = Depends(get_attend_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Відвідування лекцій студентом
    body = {
                href: location.href ,
                referrer: document.referrer,
                duration: duration
            }
    """
    logs = db.query(Log).filter(Log.username == username).all()
    for log in logs:
        obj = json.loads(log.body)
        log.lec = obj['href']
        log.duration = obj['duration']

    
    return templates.TemplateResponse("stat/visits.html", {"request": request, "logs": logs})

# # -------------------------- new -------------------------

# @router.get("/new")
# async def get_attend_new (
#     request: Request, 
#     db: Session = Depends(get_attend_db),
#     user: User = Depends(get_current_tutor)
# ):
#     """ 
#     Новий розклад.
#     """
#     shadule = Shadule(classes="", moments="") 
#     return templates.TemplateResponse("attend/edit.html", {"request": request, "shadule": shadule})

# @router.post("/new")
# async def post_attend_new(
#     request: Request,
#     classes: str = Form(...),
#     moments: str = Form(""),
#     db: Session = Depends(get_attend_db),
#     user: User = Depends(get_current_tutor)
# ):
#     shadule = Shadule(
#         classes = classes,
#         moments = moments,
#         username = user.username,
#     )

#     # check if moments are correct
#     if (mes := shadule.moments_ok()) != "ok":
#         shadule.moments = f"{mes}\n{shadule.moments}"
#         return templates.TemplateResponse("attend/edit.html", {"request": request, "shadule": shadule})
    
#     try:
#         db.add(shadule) 
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         return templates.TemplateResponse("attend/edit.html", {"request": request, "shadule": shadule})
#     return RedirectResponse(url="/attend/list", status_code=302)

# # -------------------------- edit -------------------------

# @router.get("/edit/{id}")
# async def get_attend_edit(
#     id: int,
#     request: Request, 
#     db: Session = Depends(get_attend_db),
#     user: User = Depends(get_current_tutor)
# ):
#     """ 
#     Редагування розкладу.
#     """
#     shadule = db.get(Shadule, id)
#     if not shadule:
#         return RedirectResponse(url="/attend/list", status_code=302)
    
#     return templates.TemplateResponse("attend/edit.html", {"request": request, "shadule": shadule})


# @router.post("/edit/{id}")
# async def post_attend_edit(
#     id: int,
#     request: Request,
#     classes: str = Form(...),
#     moments: str = Form(""),
#     db: Session = Depends(get_attend_db),
#     user: User = Depends(get_current_tutor)
# ):
#     shadule = db.get(Shadule, id)
#     if not shadule:
#         raise HTTPException(404, f"Not found shadule_id={id} in DB.")
#     shadule.classes = classes
#     shadule.moments = moments
    
#     # check if moments are correct
#     if (mes := shadule.moments_ok()) != "ok":
#         shadule.moments = f"{mes}\n{shadule.moments}"
#         return templates.TemplateResponse("attend/edit.html", {"request": request, "shadule": shadule})
    
#     db.commit()
#     return RedirectResponse(url="/attend/list", status_code=302)

# # ------- del 

# @router.get("/del/{id}")
# async def get_attend_del(
#     id: int, 
#     request: Request, 
#     db: Session = Depends(get_attend_db),
#     user: User = Depends(get_current_tutor)
# ):
#     """ 
#     Видалення розкладу.
#     """
#     shadule = db.get(Shadule, id)
#     if not shadule:
#         return RedirectResponse(url="/attend/list", status_code=302)
    
#     return templates.TemplateResponse("attend/del.html", {"request": request, "shadule": shadule})


# @router.post("/del/{id}")
# async def post_attend_del(
#     id: int,
#     db: Session = Depends(get_attend_db),
#     user: User = Depends(get_current_tutor)
# ):
#     shadule = db.get(Shadule, id)
#     db.delete(shadule)
#     db.commit()
#     return RedirectResponse(url="/attend/list", status_code=302)

# # ---------------------------- Snapshot (AJAX) ------------------------

# API_KEY = "secret123"

# class SnapshotRequest(BaseModel):
#     username: str
#     visitors: list[str]

# @router.post("/snapshot")
# async def post_snapshot(
#     data: SnapshotRequest,
#     db: Session = Depends(get_attend_db)
# ):
#     snapshot = Snapshot(
#         username = data.username,
#         visitors = ",".join(data.visitors),  
#         when = datetime.now()
#     )
#     db.add(snapshot)
#     db.commit()
#     return {"status": "ok"}

# # --------------------------attend report -------------------------

# @router.get("/report/{classes}")
# async def get_attend_report(
#     request: Request,
#     classes: str,
#     db: Session = Depends(get_attend_db),
#     user: User = Depends(get_current_tutor)
# ):
#     """ 
#     Матриця відвідування занять (classes).
#     """
#     shadule = db.query(Shadule).filter(Shadule.username == user.username).filter(Shadule.classes == classes).one_or_none()
#     shots = db.query(Snapshot).filter(Snapshot.username == user.username).all()
#     names, begins, matrix = create_matrix(shadule, shots)
#     v_headers = [(beg, beg.strftime("%d/%m")) for beg in begins]

#     names = sorted([change(n) for n in names])

#     return templates.TemplateResponse("attend/report.html", {"request": request, 
#         "names": names, "v_headers":v_headers, "matrix": matrix, "classes": shadule.classes})

# def change(name):
#     """John Doe -> Doe John"""
#     first, last = name.split()
#     return f"{last} {first}"

