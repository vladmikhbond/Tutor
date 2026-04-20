import os
from typing import List
from fastapi.security import APIKeyCookie
import jwt

from fastapi import APIRouter, HTTPException, Request, Form, Response, Security, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import dal
from .token_router import authenticated_user, create_access_token

from ..models.pset_models import User
from ..models.schemas import HelpItem

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_LIFETIME = int(os.getenv("TOKEN_LIFETIME", "180"))

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- login

@router.get("/")
async def get_login(request: Request):
    return templates.TemplateResponse(request, "login/login.html")


@router.post("/")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(dal.get_users_db),
):
    # Authenticate locally using DB + helpers from token_router
    user = authenticated_user(db, username, password)
    if user is None:
        return templates.TemplateResponse(request, "login/login.html", {
            "error": "Invalid credentials." })

    token = create_access_token(payload={"sub": username, "role": user.role})

    redirect = RedirectResponse("/disc/list", status_code=302)

    # Встановлюємо cookie у відповідь
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,        # ❗ Забороняє доступ з JS
        # secure=True,        # ❗ Передавати лише по HTTPS
        samesite="lax",       # ❗ Захист від CSRF
        max_age=TOKEN_LIFETIME * 60,  # in seconds 
    )
    return redirect    

@router.get("/login/logout")
async def logout(request: Request):
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("access_token", path="/")
    return resp

# -------------------------- help

@router.get("/login/help")
async def help(request: Request):
    """
    Читає вміст файлу app/static/help/help.txt в список HelpItem.
    В head рядок без відступу, в body рядки з відступом.
    """
    items: List[HelpItem] = []
    with open("app/static/help/help.txt", "r", encoding="utf-8") as f:
        current_item = None
        for line in f:
            line = line.rstrip('\n')
            if line and line[0] != ' ':  # is a head
                if current_item is not None:
                    items.append(current_item)
                current_item = HelpItem(head=line, body=[])
            elif line and current_item is not None:  # is a body
                current_item.body.append(line.strip())
        if current_item is not None:
            items.append(current_item)
    

    return templates.TemplateResponse(request, "login/help.html", {"items": items})
    

# ---------------------------- aux


# Containeer of the token is cookie
cookie_scheme = APIKeyCookie(name="access_token")

def get_current_user(token: str = Security(cookie_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    else:
        return User(username=payload.get("sub"), role=payload.get("role"))


def get_current_tutor(token: str = Security(cookie_scheme)) -> User:
    user = get_current_user(token)
    if user.role != "tutor":
        raise HTTPException(status_code=403, detail="Permission denied: tutors only.")
    return user

# ----------------------- Зміна паролю

@router.get("/pass")
async def get_pass(
    request: Request, 
    user: User = Depends(get_current_user) 
):
    return templates.TemplateResponse(request, "login/pass.html")

@router.post("/pass")
async def post_pass (
    request: Request,
    password: str = Form(...),
    db: Session = Depends(dal.get_users_db),
    current_user: User = Depends(get_current_user) 
):
    user = db.get(User, current_user.username);
    if not user:
        raise HTTPException(400)
    user.hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        db.commit()
    except:
        error = "Не вдалося змінити пароль"
        return templates.TemplateResponse(request, "login/pass.html", {"error": error}) 

    html = f'Пароль змінено на "{password}". Для продовження роботи <a href="/">увійдіть з новим паролем</a>.'
    return HTMLResponse(content=html, status_code=200)
