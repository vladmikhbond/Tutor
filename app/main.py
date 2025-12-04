from fastapi import FastAPI
from .routers import login_router, disc_router, lecture_router, user_router, filter_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(login_router.router, tags=["login"])
app.include_router(disc_router.router, prefix="/disc", tags=["disc"])
app.include_router(lecture_router.router, prefix="/lecture", tags=["lecture"])
app.include_router(user_router.router, prefix="/user", tags=["user"])
app.include_router(filter_router.router, prefix="/filter", tags=["filter"])

