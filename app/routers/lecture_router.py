import datetime as dt
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from ..models.models import Disc, Lecture, User

from .login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД


# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- list

@router.get("/list/{disc_id}")
async def get_lecture_list(
    request: Request, 
    disc_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """ 
    Усі лекції із згаданої дисципліни.
    """   
    disc = db.get(Disc, disc_id)

    return templates.TemplateResponse("lecture/list.html", 
            {"request": request, "disc": disc})


# ------- new 

@router.get("/new/{disc_id}")
async def get_lecture_new(
    request: Request,
    disc_id: int,
    username: str = Depends(get_current_user)
):
    """ 
    Створення нової лекції.
    """
    lecture = Lecture(title="", content="") 
    return templates.TemplateResponse("lecture/new.html", {"request": request, "lecture": lecture})


@router.post("/new/{disc_id}")
async def post_lecture_new(
    request: Request,
    disc_id: int,
    title: str = Form(...),
    content: str = Form(...),
    is_public: bool = Form(...),
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    lecture = Lecture(
        title = title,
        content = content, 
        is_public = is_public,
        disc_id = disc_id,
        modified = dt.datetime.now()
    )
    try:
        db.add(lecture) 
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a new lecture adding: {e}"
        return templates.TemplateResponse("lecture/new.html", {"request": request, "lecture": lecture})
    return RedirectResponse(url="/lecture/list", status_code=302)

# # ------- edit 

# @router.get("/edit/{id}")
# async def get_lecture_edit(
#     id: int, 
#     request: Request, 
#     db: Session = Depends(get_db),
#     username: str=Depends(get_current_user)
# ):
#     """ 
#     Редагування дисципліни.
#     """
#     lecture = db.get(lecture, id)
#     if not lecture:
#         return RedirectResponse(url="/lecture/list", status_code=302)
#     return templates.TemplateResponse("lecture/edit.html", {"request": request, "lecture": lecture})


# @router.post("/edit/{id}")
# async def post_lecture_edit(
#     id: int,
#     request: Request,
#     title: str = Form(...),
#     lang: str = Form(...),
#     theme: str = Form(...),
#     db: Session = Depends(get_db),
#     username: str=Depends(get_current_user)
# ):
#     lecture = db.get(lecture, id)
#     if not lecture:
#         return RedirectResponse(url="/lecture/list", status_code=302)
#     lecture.title = title
#     lecture.lang = lang 
#     lecture.theme= theme
#     db.commit()
#     return RedirectResponse(url="/lecture/list", status_code=302)
   
# # ------- del 

# @router.get("/del/{id}")
# async def get_lecture_del(
#     id: int, 
#     request: Request, 
#     db: Session = Depends(get_db),
#     username: str=Depends(get_current_user)
# ):
#     """ 
#     Видалення дисципліни.
#     """
#     lecture = db.get(lecture, id)
#     if not lecture:
#         return RedirectResponse(url="/lecture/list", status_code=302)
    
#     return templates.TemplateResponse("lecture/del.html", {"request": request, "lecture": lecture})


# @router.post("/del/{id}")
# async def post_lecture_del(
#     id: int,
#     request: Request,
#     db: Session = Depends(get_db),
#     username: str=Depends(get_current_user)
# ):
#     lecture = db.get(lecture, id)
#     db.delete(lecture)
#     db.commit()
#     return RedirectResponse(url="/lecture/list", status_code=302)


