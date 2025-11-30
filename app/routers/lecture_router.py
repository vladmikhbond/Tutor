import re
import datetime as dt
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from ..models.models import Disc, Lecture, Picture

from .login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД
from ..lectorium.main import translate, get_style

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
    lecture = Lecture(content="🔴1 Noname") 
    return templates.TemplateResponse("lecture/new.html", 
            {"request": request, "lecture": lecture, "disc_id": disc_id})


@router.post("/new/{disc_id}")
async def post_lecture_new(
    request: Request,
    disc_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):  
    
    lecture = Lecture(
        content = content, 
        is_public = False,
        disc_id = disc_id,
        modified = dt.datetime.now()
    )
    db.add(lecture) 
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()   
        raise HTTPException(500, "Fail to create a new lecture.")
    
    return RedirectResponse(url=f"/lecture/edit/{lecture.id}", status_code=302)

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

@router.post("/edit/{id}")      # ajax
async def post_lecture_edit(
    id: int,
    request: Request,
    content: str = Form(...),
    is_public: bool = Form(default=False),
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    lecture = db.get(Lecture, id)


    if not lecture:
        raise HTTPException(404)
    
    lecture.content = content
    lecture.is_public = is_public
    lecture.modified = dt.datetime.now()

    try:
        db.commit()
    except Exception as e:
        db.rollback()   
        raise HTTPException(500, "Fail to change the lecture.")
  
    return {"status": "OK"}

   
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
        raise HTTPException(404, f"No lecture with id={id}")

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
    Отримує лекцію з БД і створює файл {disc.title}.html і папку pic в папці app/static/output
    """
    lecture = db.get(Lecture, id)
    if not lecture:
        raise HTTPException(404, f"No lecture with id={id}")
    
    title = export_lecture(lecture, "app/static/output", db)

    url=f"/static/output/{title}.html"
    return RedirectResponse(url, status_code=302)

def export_lecture(lecture: Lecture, dst:str, db:Session):

    # create file {lect_title}.html
    title, html = translate(lecture.content, lecture.disc.lang, lecture.disc.theme)
    title_url = tune(title)
    with open(f"{dst}/{title_url}.html", "w") as f:
        f.write(html)
    
    # create folder pic
    lines = get_style(lecture.content, 2)
    pictures: List[Picture] = db.query(Picture).filter(
            Picture.disc_id == lecture.disc_id and Picture.title in lines).all()
    for picture in pictures:
        with open(f"{dst}/pic/{picture.title}", "bw") as f:
            f.write(picture.image)
    return title_url

def tune(line: str) -> str:
    """
    Прибирає з рядка символои, не бажані в URL
    """
    forbiddens = " <>\"{}|\\^`[]':/?#[]@!$&'()*+,;="
    lst = ['_' if c in forbiddens else c  for c in line]
    return ''.join(lst);
     


# ----------------------- search in 

@router.post("/search/{disc_id}")
async def post_lecture_picture(
    disc_id: str,
    request: Request,
    sample: str = Form(...),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """
    Пошук зразка в чернетках лекцій.
    """
    lectures = db.get(Disc, disc_id).lectures 
    finded = []
    for lec in lectures:
        text = lec.content.replace('\r', '')
        positions = [m.start() for m in re.finditer(sample, text)]
        DELTA = 60
        for pos in positions:
            end = pos + len(sample)
            finded.append({
                "before": text[pos - DELTA : pos],
                "after": text[end : end + DELTA],
                "pos": pos,
                "end": end,
                "lec_id": lec.id
            })
    return templates.TemplateResponse("lecture/search.html", {"request": request, "finded": finded, "sample": sample})
