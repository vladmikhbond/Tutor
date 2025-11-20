from fastapi import FastAPI
from .routers import login_router, disc_router, lecture_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(login_router.router, tags=["login"])
app.include_router(disc_router.router, prefix="/disc", tags=["disc"])
app.include_router(lecture_router.router, prefix="/lecture", tags=["lecture"])

