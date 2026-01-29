
from datetime import datetime
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.models.pset_models import User
from app.routers.login_router import get_current_tutor

from ..models.attend_models import Shadule, Snapshot
from ..dal import get_attend_db

router = APIRouter()

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

# ---------------------------- Snapshot (AJAX) ------------------------

API_KEY = "secret123"

class SnapshotRequest(BaseModel):
    username: str
    visitors: list[str]

@router.post("/snapshot")
async def post_snapshot(
    data: SnapshotRequest,
    db: Session = Depends(get_attend_db)
):
    snapshot = Snapshot(
        username = data.username,
        visitors = ",".join(data.visitors),  
        when = datetime.now()
    )
    db.add(snapshot)
    db.commit()
    return {"status": "ok"}

# -------------------------- list -------------------------
@router.get("/list")
async def get_attend_list(
    request: Request, 
    db: Session = Depends(get_attend_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Редагування розкладу.
    """
    shadules = db.query(Shadule).filter(Shadule.username == user.username).all()
    return templates.TemplateResponse("attend/list.html", {"request": request, "shadules": shadules})


# -------------------------- edit -------------------------



@router.get("/edit")
async def get_attend_edit(

    request: Request, 
    db: Session = Depends(get_attend_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Редагування розкладу.
    """
    shadules = db.query(Shadule).filter(Shadule.username == user.username).all()
    txt = '\n'.join([s])
    return templates.TemplateResponse("attend/edit.html", {"request": request, "": disc, "colors": colors})


# @router.post("/edit/{id}")
# async def post_disc_edit(
#     id: int,
#     request: Request,
#     title: str = Form(...),
#     lang: str = Form(...),
#     db: Session = Depends(get_db),
#     user: User = Depends(get_current_tutor)
# ):
#     # colors from request form
#     form = await request.form()
#     colors = {}
#     for name in COLOR_NAMES:
#         colors[name] = form.get(name)

#     disc = db.get(Disc, id)
#     if not disc:
#         raise HTTPException(404, f"Saving changes of disc id={id} is failed.")


#     disc.title = title
#     disc.lang = lang 
#     disc.theme = json.dumps(colors)
#     db.commit()
#     return RedirectResponse(url="/disc/list", status_code=302)

