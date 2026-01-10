from fastapi import FastAPI
from .routers import login_router, disc_router, lecture_router, user_router, token_router
from fastapi.staticfiles import StaticFiles
import os
import jwt
from .models.pss_models import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.middleware("http")
async def attach_current_user(request, call_next):
    """Attach current user (if any) to request.state.user by decoding access_token cookie."""
    token = request.cookies.get("access_token")
    request.state.user = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user = User(username=payload.get("sub"), role=payload.get("role"))
        except Exception:
            request.state.user = None
    response = await call_next(request)
    return response

app.include_router(login_router.router, tags=["login"])
app.include_router(disc_router.router, prefix="/disc", tags=["disc"])
app.include_router(lecture_router.router, prefix="/lecture", tags=["lecture"])
app.include_router(user_router.router, prefix="/user", tags=["user"])
app.include_router(token_router.router, prefix="/token", tags=["token"])

