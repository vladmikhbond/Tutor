import os
import shutil
import io
import zipfile
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.models.pset_models import User

from ..models.models import Disc, Lecture, Picture
from ..routers.login_router import get_current_tutor
from ..dal import get_db  # Функція для отримання сесії БД
from ..lectorium.converter import convert, tune
from ..routers.lecture_router import export_lecture

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

COLOR_NAMES = ["body", "header", "text", "bg", "link", "aux"]
DEFAULT_LIGHT_COLORS = {
    "body": "#edf2f8", "header": "#0000ff", "text": "#000080", 
    "bg": "#e6eef5", "link": "#d3589b", "aux": "#ffffff"
}

# ----------------------- list

@router.get("/list")
async def get_disc_list(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Усі дисципліни користувача.
    """   
    discs = db.query(Disc).filter(Disc.username == user.username).all()

    return templates.TemplateResponse("disc/list.html", 
            {"request": request, "discs": discs})



# ------- new

@router.get("/new")
async def get_disc_new(
    request: Request,
    user: User = Depends(get_current_tutor)
):
    """ 
    Створення нової дисципліни.
    """
    disc = Disc(title="", lang="", theme="") 
    colors = DEFAULT_LIGHT_COLORS
    return templates.TemplateResponse("disc/edit.html", {"request": request, "disc": disc, "colors": colors})


@router.post("/new")
async def post_disc_new(
    request: Request,
    title: str = Form(...),
    lang: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    # colors from request form
    form = await request.form()
    colors = {}
    for name in COLOR_NAMES:
        colors[name] = form.get(name)

    disc = Disc(
        title = title,
        theme = json.dumps(colors), 
        lang = lang,
        username = user.username,
    )
    try:
        db.add(disc) 
        db.commit()
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("disc/edit.html", {"request": request, "disc": disc})
    return RedirectResponse(url="/disc/list", status_code=302)

# ------- edit 

@router.get("/edit/{id}")
async def get_disc_edit(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Редагування дисципліни.
    """
    disc = db.get(Disc, id)
    if not disc:
        return RedirectResponse(url="/disc/list", status_code=302)
    try:
        colors = json.loads(disc.theme)
    except: 
        colors = DEFAULT_LIGHT_COLORS
    return templates.TemplateResponse("disc/edit.html", {"request": request, "disc": disc, "colors": colors})


@router.post("/edit/{id}")
async def post_disc_edit(
    id: int,
    request: Request,
    title: str = Form(...),
    lang: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    # colors from request form
    form = await request.form()
    colors = {}
    for name in COLOR_NAMES:
        colors[name] = form.get(name)

    disc = db.get(Disc, id)
    if not disc:
        raise HTTPException(404, f"Saving changes of disc id={id} is failed.")


    disc.title = title
    disc.lang = lang 
    disc.theme = json.dumps(colors)
    db.commit()
    return RedirectResponse(url="/disc/list", status_code=302)
   
# ------- del 

@router.get("/del/{id}")
async def get_disc_del(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Видалення дисципліни.
    """
    disc = db.get(Disc, id)
    if not disc:
        return RedirectResponse(url="/disc/list", status_code=302)
    
    return templates.TemplateResponse("disc/del.html", {"request": request, "disc": disc})


@router.post("/del/{id}")
async def post_disc_del(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    disc = db.get(Disc, id)
    db.delete(disc)
    db.commit()
    return RedirectResponse(url="/disc/list", status_code=302)

# ------- saving

@router.get("/save/{id}")
async def get_save(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Збереження дисципліни.
    """
    disc = db.get(Disc, id)
    if not disc:
        raise HTTPException(404, f"Saving of disc id={id} is failed.")    
    return save_zip(disc, db) 


def save_zip(disc: Disc, db: Session):
    buffer = io.BytesIO()
    disc.lectures.sort(key = lambda l: l.title)

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Запакувати лекції         
        for lecture in disc.lectures:
            tuned_title = tune(lecture.title)
            zf.writestr(tuned_title + ".txt", lecture.content)
        # Запакувати малюнки
        pictures: List[Picture] = db.query(Picture).filter(Picture.disc_id == lecture.disc_id ).all()
        for picture in pictures:
            zf.writestr(f"pic/{picture.title}", picture.image)

    # Повернути файл [назва_дисципліни].txt.zip
    buffer.seek(0)
    return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={tune(disc.title)}.txt.zip"}
        )



# ------- export

@router.get("/export/{id}")
async def get_export(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Експорт дисципліни у вигляді zip файлу.
    """
    disc = db.get(Disc, id)
    if not disc:
        raise HTTPException(404, f"Export of disc id={id} is failed.")
    return zip_disc(disc, db) 


def zip_disc(disc: Disc, db: Session):
    # Get the public lectures only
    lectures = db.query(Lecture).filter(Lecture.disc_id == disc.id).filter(Lecture.is_public).all()
    lectures.sort(key = lambda l: l.title)
    
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:        
        # Запакувати лекції
        for lecture in lectures:
            html = convert(lecture.content, lecture.disc.lang, lecture.disc.theme, version="student")
            tuned_title = tune(lecture.title)
            zf.writestr(tuned_title + ".html", html)

        # Створити і запакувати індекс
        FAKE_HTTP = "http://"
        index_content = f"@2 {disc.title}\n"
        for lecture in lectures:
            index_content += f"@3 [[{FAKE_HTTP}{tune(lecture.title)}.html|{lecture.title}]]\n"
        index_html = convert(index_content, disc.lang, disc.theme, version="student")
        index_html = index_html.replace(FAKE_HTTP, "")
        zf.writestr("index.html", index_html)
        
        # Запакувати малюнки
        pictures: List[Picture] = db.query(Picture).filter(Picture.disc_id == Picture.disc_id ).all()
        for picture in pictures:
            zf.writestr(f"pic/{picture.title}", picture.image)
        
        # Допакувти папку sys
        zip_sys(zf)
        
    # Повернути ZIP із назвою дисципліни
    buffer.seek(0)
    return StreamingResponse(
            buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={tune(disc.title)}.zip"}
        )

def zip_sys(zf):

    def arc(name):
        with open(f"app/static/output/sys/{name}", "r", encoding="utf-8") as f:
            text = f.read()
        zf.writestr(f"sys/{name}", text)

    arc("engine.css")
    arc("engine.js")
    zf.write("app/static/output/sys/pic/pensil.png", "sys/pic/pensil.png")

# --------------------------- clear output
   
@router.get("/clear")
async def get_disc_clear(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_tutor)
):
    """ 
    Спустошує вихідну папку. Залишає в ній підпапку sys і файл _sample_.html.
    """   
    return remove_files("app/static/output")

def remove_files(path):
    count_files = 0
    for root, dirs, files in os.walk(path):  
        for file in files:
            if root.endswith("/sys") or root.endswith("/sys/pic") or file == "_sample_.html":
                continue
            os.remove(os.path.join(root, file)) 
            count_files += 1
    return count_files






