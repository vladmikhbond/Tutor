from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from ..models.models import Disc, User

from ..routers.login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД

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
    return templates.TemplateResponse("disc/new.html", {"request": request, "disc": disc})


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
        return templates.TemplateResponse("disc/new.html", {"request": request, "disc": disc})
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
        return RedirectResponse(url="/disc/list", status_code=302)
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
    request: Request,
    db: Session = Depends(get_db),
    username: str=Depends(get_current_user)
):
    disc = db.get(Disc, id)
    db.delete(disc)
    db.commit()
    return RedirectResponse(url="/disc/list", status_code=302)


