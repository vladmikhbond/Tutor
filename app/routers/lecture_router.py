
import datetime as dt
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from ..models.models import Disc, Lecture, Picture

from .login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД
from ..lectorium.main import translate, get_title, get_style

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
    lecture = Lecture(title="Noname", content="") 
    return templates.TemplateResponse("lecture/edit.html", 
            {"request": request, "lecture": lecture, "disc_id": disc_id})


@router.post("/new/{disc_id}")
async def post_lecture_new(
    request: Request,
    disc_id: int,
    content: str = Form(...),
    is_public: bool = Form(default=False),
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):  
    lecture = Lecture(
        title = get_title(content),
        content = content, 
        is_public = is_public,
        disc_id = disc_id,
        modified = dt.datetime.now()
    )
    db.add(lecture) 

    try:
        db.commit()
    except Exception as e:
        db.rollback()   
        return templates.TemplateResponse("lecture/edit.html", {"request": request, "lecture": lecture})
    
    return RedirectResponse(url=f"/lecture/list/{disc_id}", status_code=302)

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
    return templates.TemplateResponse("lecture/edit.html", 
            {"request": request, "lecture": lecture, "disc_id": lecture.disc_id})

@router.post("/edit/{id}")
async def post_lecture_edit(
    id: int,
    request: Request,
    content: str = Form(...),
    is_public: bool = Form(default=False),
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    lecture = db.get(Lecture, id)
    disc_id = lecture.disc_id

    if not lecture:
        return HTTPException(404)

    lecture.title = get_title(content)
    lecture.content = content
    lecture.is_public = is_public
    lecture.modified = dt.datetime.now()


    try:
        db.commit()
    except Exception as e:
        db.rollback()   
        return templates.TemplateResponse("lecture/edit.html", {"request": request, "lecture": lecture})
  
  
    return RedirectResponse(url=f"/lecture/list/{disc_id}", status_code=302)
   
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

    
# --------------------- picture 

@router.post("/picture")
async def post_lecture_picture(
    file: UploadFile = File(...),
    disc_id: int = Form(...),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """
    Завантажити зображення для дисципліни.
    """
    if not file:
        return {"error": "No file provided"}
    image = await file.read()    
    disc = db.get(Disc, disc_id)
    if not disc:
        return {"error": f"Disc with id={disc_id} not found"}
    try:   
        existing_pictures = list(filter(lambda p: p.title == file.filename,  disc.pictures))
        if len(existing_pictures):
            existing_pictures[0].image = image
        else:
            picture = Picture (
                title=file.filename,
                disc_id=disc_id,
                image=image
            )
            db.add(picture)
        db.commit()       
        return {"filename": file.filename}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

# ----------------------- trans 

@router.get("/trans/{id}")
async def get_lecture_trans(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    """ 
    Трансляція лекції.
    Отримує лекцію з БД і створює файл temp.html і папку pic в папці app/static/output
    """
    lecture = db.get(Lecture, id)
    if not lecture:
        return HTTPException(404, f"No lecture with id={id}")
    
    # file temp.html
    work = translate(lecture.content, lecture.disc.theme, lecture.disc.lang)
    with open(f"app/static/output/temp.html", "w") as f:
        f.write(work)
    # folder pic
    lines = get_style(lecture.content, 2)
    pictures: List[Picture] = db.query(Picture).filter(
            Picture.disc_id == lecture.disc_id and Picture.title in lines).all()
    for picture in pictures:
        with open(f"app/static/output/pic/{picture.title}", "bw") as f:
            f.write(picture.image)

    url=f"/static/output/temp.html"
    return RedirectResponse(url, status_code=302)
