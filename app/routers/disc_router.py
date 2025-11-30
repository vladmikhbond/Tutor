import os
import shutil
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from ..models.models import Disc, Picture

from ..routers.login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД

from ..lectorium.main import translate, get_style
from ..routers.lecture_router import export_lecture

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- list

@router.get("/list")
async def get_disc_list(
    request: Request, 
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """ 
    Усі дисципліни користувача.
    """   
    discs = db.query(Disc).filter(Disc.username == username).all()

    return templates.TemplateResponse("disc/list.html", 
            {"request": request, "discs": discs})


# ------- new 

@router.get("/new")
async def get_disc_new(
    request: Request,
    username: str = Depends(get_current_user)
):
    """ 
    Створення нової дисципліни.
    """
    disc = Disc(title="", lang="", theme="") 
    return templates.TemplateResponse("disc/edit.html", {"request": request, "disc": disc})


@router.post("/new")
async def post_disc_new(
    request: Request,
    title: str = Form(...),
    lang: str = Form(...),
    theme: str = Form(...),
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    disc = Disc(
        title = title,
        theme = theme, 
        lang = lang,
        username = username,
    )
    try:
        db.add(disc) 
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a new disc adding: {e}"
        return templates.TemplateResponse("disc/edit.html", {"request": request, "disc": disc})
    return RedirectResponse(url="/disc/list", status_code=302)

# ------- edit 

@router.get("/edit/{id}")
async def get_disc_edit(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    """ 
    Редагування дисципліни.
    """
    disc = db.get(Disc, id)
    if not disc:
        return RedirectResponse(url="/disc/list", status_code=302)
    return templates.TemplateResponse("disc/edit.html", {"request": request, "disc": disc})


@router.post("/edit/{id}")
async def post_disc_edit(
    id: int,
    request: Request,
    title: str = Form(...),
    lang: str = Form(...),
    theme: str = Form(...),
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    disc = db.get(Disc, id)
    if not disc:
        raise HTTPException(404, f"Saving changes of disc id={id} is failed.")
    disc.title = title
    disc.lang = lang 
    disc.theme= theme
    db.commit()
    return RedirectResponse(url="/disc/list", status_code=302)
   
# ------- del 

@router.get("/del/{id}")
async def get_disc_del(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
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
    username: str=Depends(get_current_user)
):
    disc = db.get(Disc, id)
    db.delete(disc)
    db.commit()
    return RedirectResponse(url="/disc/list", status_code=302)


# ------- export

@router.get("/export/{id}")
async def get_export_del(
    id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    """ 
    Експорт дисципліни.
    """
    disc = db.get(Disc, id)
    if not disc:
        raise HTTPException(404, f"Export of disc id={id} is failed.")
    
    return export_disc(disc, db) 


def export_disc(disc: Disc, db: Session):

    sys = "app/static/output/sys"
    dst = f"app/export/{disc.title}"

    # Якщо папка {disc.title} вже існує — видалити 
    if os.path.exists(dst):
        shutil.rmtree(dst)
    
    # Створити папку з підпапками sys і pic
    os.mkdir(dst)
    shutil.copytree(sys, f"{dst}/sys")
    os.mkdir(dst + "/pic")
    
    # Зберігти лекції 
    index_content = f"@2 {disc.title}\n"
    for lecture in disc.lectures:
        tuned_title = export_lecture(lecture, dst, db)
        index_content += f"@3 [[http://{tuned_title}.html|{lecture.title}]]\n"
    
    # Зберігти індекс
    html = translate(index_content, disc.lang, disc.theme)

    html = html.replace("http://", "")  
    fname = f"{dst}/index.html"
    with open(fname, "w") as f:
        f.write(html)
    return fname
# ----------------------------------------------------------------
# not used yet
def clear_output_folder():
    """
    Видаляє усе, крім папки sys. Папку pic спустошуємо. 
    """
    folder = "app/static/output"
    exclude = "sys"

    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if name == exclude:
            continue
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    os.mkdir(folder + "/pic")

