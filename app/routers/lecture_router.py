import datetime as dt
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from ..models.models import Disc, Lecture, User

from .login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД
from ..lectorium.main import trans

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
    url=f"/lecture/list/{disc_id}"
    try:
        db.add(lecture) 
        db.commit()
    except Exception as e:
        db.rollback()
        
        return templates.TemplateResponse("lecture/new.html", {"request": request, "lecture": lecture})
    return RedirectResponse(url, status_code=302)

# ------- edit 

@router.get("/edit/{id}")
async def get_lecture_edit(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    """ 
    Редагування лекції.
    """
    lecture = db.get(Lecture, id)
    if not lecture:
        return RedirectResponse(url=f"/lecture/list/{lecture.disc_id}", status_code=302)
    return templates.TemplateResponse("lecture/edit.html", {"request": request, "lecture": lecture})


@router.post("/edit/{id}")
async def post_lecture_edit(
    id: int,
    title: str = Form(...),
    content: str = Form(...),
    is_public: bool = Form(...),
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    lecture = db.get(Lecture, id)
    url=f"/lecture/list/{lecture.disc_id}"

    if not lecture:
        return RedirectResponse(url=url, status_code=302)
    lecture.title = title
    lecture.content = content
    lecture.is_public = is_public
    lecture.modified = dt.datetime.now()
    db.commit()

    # ##########################################################################
    body, fname = trans(lecture.content, theme="github", lang="javascript")
    with open(f"/workspaces/Tutor/app/static/output/work.html", "w") as f:
        f.write(body)
    # ##########################################################################

    return RedirectResponse(url=url, status_code=302)
   
# ------- del 

@router.get("/del/{id}")
async def get_lecture_del(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    """ 
    Видалення лекції.
    """
    lecture = db.get(Lecture, id)
    if not lecture:
        return HTTPException(404, f"No lecture with id={id}")

    return templates.TemplateResponse("lecture/del.html", {"request": request, "lecture": lecture})


@router.post("/del/{id}")
async def post_lecture_del(
    id: int,
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    lecture = db.get(Lecture, id)
    db.delete(lecture)
    db.commit()

    url=f"/lecture/list/{lecture.disc_id}"
    return RedirectResponse(url, status_code=302)


