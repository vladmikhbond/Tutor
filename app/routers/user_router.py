import re
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.routers.filter_router import get_user_filter
from ..models.user_models import User
from .login_router import get_current_tutor
from ..dal import get_users_db  # Функція для отримання сесії БД



# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- list

@router.get("/list")
async def get_user_list(
    request: Request, 
    db: Session = Depends(get_users_db),
    username: str = Depends(get_current_tutor)
):
    """ 
    Усі відфільтровані користувачи.
    """  
    users = db.query(User).all()
    filter = get_user_filter(request) 

    if filter:
        users = [u for u in users if re.search(filter, u.username, re.RegexFlag.U) is not None] 
    users.sort(key=lambda u: u.username)

    return templates.TemplateResponse("user/list.html", 
            {"request": request, "users": users, "filter_val": filter})

# ----------------------- reset password

@router.get("/reset/{name}")
async def get_user_reset(
    name: str, 
    request: Request, 
    db: Session = Depends(get_users_db),
    username: str=Depends(get_current_tutor)
):
    """ 
    Скидання паролю.
    """
    user = db.get(User, name)
    if not user:
        return RedirectResponse(url="/user/list", status_code=302)
    
    return templates.TemplateResponse("user/reset.html", {"request": request, "user": user})


@router.post("/reset/{name}")
async def post_user_reset(
    name: str, 
    db: Session = Depends(get_users_db),
    username: str=Depends(get_current_tutor)
):
    user = db.get(User, name)
    if user.role == "student":
        user.hashed_password = bcrypt.hashpw(b"123456", bcrypt.gensalt()) 
    else:
        user.hashed_password = bcrypt.hashpw(b"12345678", bcrypt.gensalt())
    db.commit()
    return RedirectResponse(url="/user/list", status_code=302)

# ------- new 

@router.get("/new")
async def get_user_new(
    request: Request,
    username: str = Depends(get_current_tutor)
):
    """ 
    Додавання нових користувачів.
    """
    return templates.TemplateResponse("user/new.html", {"request": request, "names": ""})


@router.post("/new")
async def post_user_new(
    request: Request,
    role: str = Form(...),
    names: str = Form(...),
    db: Session = Depends(get_users_db),
    username: str=Depends(get_current_tutor)
):
    arr_names = names.splitlines()
    if role == "student":
        hp = bcrypt.hashpw(b"123456", bcrypt.gensalt()) 
    else:
        hp = bcrypt.hashpw(b"12345678", bcrypt.gensalt())
    for name in arr_names:
        user = User(username=name.strip(), hashed_password=hp, role=role)
        db.add(user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        err_mes = f"Error during a new disc adding: {e}"
        return templates.TemplateResponse("user/new.html", {"request": request, "names": names})
    return RedirectResponse(url="/user/list", status_code=302)


# ------- del 

@router.get("/del/{name}")
async def get_user_del(
    name: str, 
    request: Request, 
    db: Session = Depends(get_users_db),
    username: str=Depends(get_current_tutor)
):
    """ 
    Видалення користувача.
    """
    user = db.get(User, name)
    if not user:
        return RedirectResponse(url="/user/list", status_code=302)
    
    return templates.TemplateResponse("user/del.html", {"request": request, "user": user})


@router.post("/del/{name}")
async def post_user_del(
    name: str,
    db: Session = Depends(get_users_db),
    username: str=Depends(get_current_tutor)
):
    user = db.get(User, name)
    db.delete(user)
    db.commit()
    return RedirectResponse(url="/user/list", status_code=302)

