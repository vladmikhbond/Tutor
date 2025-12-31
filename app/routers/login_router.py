import os

from fastapi.security import APIKeyCookie
import httpx
import jwt

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Request, Form, Response, Security
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..models.pss_models import User

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
):
    url = f"{request.url}token/"
    data = {"username": username, "password": password}

    client = httpx.AsyncClient()
    try:
        response = await client.post(url, data=data)
    except httpx.RequestError as e:
        raise HTTPException(500, e)
    finally:
        await client.aclose()

    if response.is_success:
        token = response.json()
    else: 
        return templates.TemplateResponse("login/login.html", {
            "request": request, 
            "error": f"Invalid credentials. Response status_code: {response.status_code}"
        })

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
    resp = templates.TemplateResponse("login/login.html", {"request": request})
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


# -------------------------------- Аналітика перегляду декцій (не використовується)


from fastapi.responses import Response
import json
import time

@router.post("/analytics/leave")
async def analytics_leave(request: Request):
    body = await request.body()

    try:
        data = json.loads(body)
    except Exception:
        data = {}

    analytics_record = {
        "timestamp": int(time.time()),
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "url": data.get("url"),
        "referrer": data.get("referrer"),
        "duration_ms": data.get("duration"),
    }

    # Тут зберігаєш у БД / файл / лог
    print(analytics_record)

    # ВАЖЛИВО: sendBeacon очікує 204 або 200 без тіла
    return Response(status_code=204)
