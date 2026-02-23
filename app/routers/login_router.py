import os

import bcrypt
from fastapi.security import APIKeyCookie
import jwt

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Request, Form, Response, Security, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import dal
from ..routers.token_router import authenticated_user, create_access_token

from ..models.pset_models import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_LIFETIME = int(os.getenv("TOKEN_LIFETIME", "180"))

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- login

@router.get("/")
async def get_login(request: Request):
    return templates.TemplateResponse("login/login.html", {"request": request})


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
        return templates.TemplateResponse("login/login.html", {
            "request": request,
            "error": "Invalid credentials."
        })

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
async def logout(request: Request, response: Response):
    
    return templates.TemplateResponse("login/help.html", {"request": request})  

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
    return templates.TemplateResponse("login/pass.html", {"request": request})

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
        return templates.TemplateResponse("login/pass.html", {"request": request, "error": error}) 

    html = f'Пароль змінено на "{password}". Для продовження роботи <a href="/">увійдіть з новим паролем</a>.'
    return HTMLResponse(content=html, status_code=200)
