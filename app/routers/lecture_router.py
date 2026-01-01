import os
import re
import datetime as dt
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, Response, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models.models import Disc, Lecture, Picture
from ..models.pss_models import User

from .login_router import get_current_tutor
from ..dal import get_db  # Функція для отримання сесії БД
from ..lectorium.converter import convert, get_style, tune

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- list

@router.get("/list/{disc_id}")
async def get_lecture_list(
    request: Request, 
    disc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Усі лекції певної дисципліни.
    """   
    disc = db.get(Disc, disc_id)
    disc.lectures.sort(key=lambda l: l.title)

    return templates.TemplateResponse("lecture/list.html", 
            {"request": request, "disc": disc})


# ------- new 

@router.get("/new/{disc_id}")
async def get_lecture_new(
    request: Request,
    disc_id: int,
    user: User = Depends(get_current_tutor)
):
    """ 
    Створення нової лекції.
    """
    return templates.TemplateResponse("lecture/new.html", 
            {"request": request, "disc_id": disc_id})


@router.post("/new/{disc_id}")
async def post_lecture_new(
    request: Request,
    disc_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
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
    user: User = Depends(get_current_tutor)
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
    user: User = Depends(get_current_tutor)
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
    user: User = Depends(get_current_tutor)
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
    user: User = Depends(get_current_tutor)
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
    user: User = Depends(get_current_tutor)
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

# ----------------------- play = translation to html

@router.get("/play/{id}")
async def get_lecture_play(
    id: int,
    slide_no: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Трансляція лекції у версії "tutor".
    Отримує лекцію з БД і створює файл [disc.title].html і папку pic в папці app/static/output
    """
    lecture = db.get(Lecture, id)
    if not lecture:
        raise HTTPException(404, f"No lecture with id={id}")
    
    lec_title = export_lecture(lecture, "app/static/output", db, "tutor", slide_no)

    url=f"/static/output/{lec_title}.html"
    return RedirectResponse(url, status_code=302)


def export_lecture(lecture: Lecture, dst_path:str, db:Session, version: str, slide_no: int):

    # create file {lect_title}.html
    html = convert(lecture.content, lecture.disc.lang, lecture.disc.theme, version, slide_no)
    tuned_title = tune(lecture.title)
    with open(f"{dst_path}/{tuned_title}.html", "w") as f:
        f.write(html)
    
    # select all picture names from the lecture
    lines = [l.lower() for l in get_style(lecture.content, 2)]

    pictures = (
        db.query(Picture)
        .filter(
            Picture.disc_id == lecture.disc_id,
            func.lower(Picture.title).in_([s.lower() for s in lines])
        )
        .all()
    )
        
    # create folder 'pic'
    for picture in pictures:
        with open(f"{dst_path}/pic/{picture.title}", "bw") as f:
            f.write(picture.image)
    return tuned_title
     

# ----------------------- search in 

@router.post("/search/{disc_id}")
async def post_lecture_picture(
    disc_id: str,
    request: Request,
    sample: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
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

# ----------------------- mark as public


@router.get("/public/{id}")
async def get_lecture_public(
    request: Request, 
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Змінити значення поля is_public на протилежне.
    """   
    lecture = db.get(Lecture, id)
    lecture.is_public = not lecture.is_public
    db.commit()
    return RedirectResponse(url=f"/lecture/list/{lecture.disc_id}", status_code=302)

# -----------------------------------------------------------------------------

@router.get("/publish/{disc_id}")
async def get_lecture_public(
    request: Request, 
    disc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Опублікувати відкриті лекції дисципліни.
    """  
    PATH_TO_PUBLIC = "/data/public/" 

    disc = db.get(Disc, disc_id)
    report = export_disc(disc, db, PATH_TO_PUBLIC + tune(disc.title))
    return Response(content=report, media_type="text/plain")


def export_disc(disc: Disc, db: Session, dst: str):

    PATH_TO_SYS = "app/static/output/sys"

    # Якщо папка дисципліни вже існує, видалити її
    if os.path.exists(dst):
        shutil.rmtree(dst)
    
    # Створити папку з підпапками sys і pic
    os.mkdir(dst)
    shutil.copytree(PATH_TO_SYS, f"{dst}/sys")
    os.mkdir(dst + "/pic")
    
    # Зберігти лекції
    report = ""
    index_content = f"@2 {disc.title}\n"
    lectures = sorted((l for l in disc.lectures), key=lambda l: l.title)
    for lecture in lectures:
        if lecture.is_public:
            tuned_title = export_lecture(lecture, dst, db, version="student", slide_no=100500)
            index_content += f"@3 [[http://{tuned_title}.html|{lecture.title}]]\n"
            report += lecture.title + "\n"
    
    # Зберігти індекс
    index_html = convert(index_content, disc.lang, disc.theme, version="student") \
                .replace("http://", "")  
    fname = f"{dst}/index.html"
    with open(fname, "w") as f:
        f.write(index_html)

    return report


