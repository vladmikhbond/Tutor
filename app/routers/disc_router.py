from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from ..models.models import Disc, User
# from app.routers.filter_router import get_filtered_questions
from ..routers.login_router import get_current_user
from ..dal import get_db  # Функція для отримання сесії БД
# from ..models.pss_models import User
# from ..models.models import Question
# from ..models.parser import parse_test_body


# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- list

@router.get("/list")
async def get_question_list(
    request: Request, 
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """ 
    Усі дисципліни користувача.
    """   
    discs = db.query(Disc).filter(Disc.username == username)

    return templates.TemplateResponse("disc/list.html", 
            {"request": request, "discs": discs})


# # ------- new 

# @router.get("/new")
# async def get_question_new(
#     request: Request,
#     user: User=Depends(get_current_tutor)
# ):
#     """ 
#     Створення нового питання.
#     """
#     question = Question(attr="", kind="", text="", answers = "") 
#     return templates.TemplateResponse("question/new.html", {"request": request, "question": question})


# @router.post("/new")
# async def post_question_new(
#     request: Request,
#     attr: str = Form(...),
#     kind: str = Form(...),
#     text: str = Form(...),
#     answers: str = Form(...),
#     db: Session = Depends(get_db),
#     user: User=Depends(get_current_tutor)
# ):
#     question = Question(
#         attr = attr,
#         kind = kind, 
#         text= text,
#         answers = answers,
#     )
#     try:
#         db.add(question) 
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         err_mes = f"Error during a new question adding: {e}"
#         return templates.TemplateResponse("question/new.html", {"request": request, "question": question})
#     return RedirectResponse(url="/question/list", status_code=302)

# # ------- edit 

# @router.get("/edit/{id}")
# async def get_question_edit(
#     id: int, 
#     request: Request, 
#     db: Session = Depends(get_db),
#     user: User=Depends(get_current_tutor)
# ):
#     """ 
#     Редагування питання.
#     """
#     question = db.get(Question, id)
#     if not question:
#         return RedirectResponse(url="/question/list", status_code=302)
#     return templates.TemplateResponse("question/edit.html", {"request": request, "question": question})


# @router.post("/edit/{id}")
# async def post_question_edit(
#     id: int,
#     request: Request,
#     attr: str = Form(...),
#     kind: str = Form(...),
#     text: str = Form(...),
#     answers: str = Form(...),
#     db: Session = Depends(get_db),
#     user: User=Depends(get_current_tutor)
# ):
#     question = db.get(Question, id)
#     if not question:
#         return RedirectResponse(url="/question/list", status_code=302)
 
#     question.attr = attr
#     question.kind = kind
#     question.text= text
#     question.answers = answers

#     db.commit()
#     return RedirectResponse(url="/question/list", status_code=302)
   
# # ------- del 

# @router.get("/del/{id}")
# async def get_question_del(
#     id: int, 
#     request: Request, 
#     db: Session = Depends(get_db),
#     user: User=Depends(get_current_tutor)
# ):
#     """ 
#     Видалення питання.
#     """
#     question = db.get(Question, id)
#     if not question:
#         return RedirectResponse(url="/question/list", status_code=302)
    
#     return templates.TemplateResponse("question/del.html", {"request": request, "question": question})


# @router.post("/del/{id}")
# async def post_question_del(
#     id: int,
#     request: Request,
#     db: Session = Depends(get_db),
#     user: User=Depends(get_current_tutor)
# ):
#     question = db.get(Question, id)
#     db.delete(question)
#     db.commit()
#     return RedirectResponse(url="/question/list", status_code=302)


# #---------------- import 

# @router.get("/question/import")
# async def get_question_import(
#     request: Request,
#     db: Session = Depends(get_db),
#     user: User=Depends(get_current_tutor)
# ):
#     """ 
#     Імпорт питань із тіла тесту. 
#     """
#     return templates.TemplateResponse("question/import.html", {"request": request})


# @router.post("/question/import")
# async def post_question_import(
#     request: Request,
#     attr: str = Form(...),
#     body: str = Form(...),
#     db: Session = Depends(get_db),
#     user: User=Depends(get_current_tutor)
# ):
#     body = body.replace('\r', '')
#     quests = parse_test_body(body, validation=True)
#     for q in quests:
#         if attr: 
#             q.attr = f"{attr}/{q.attr}"
#     db.add_all(quests)    
#     db.commit()
#     return templates.TemplateResponse("question/import.html", {"request": request})

# #---------------- export 

# @router.get("/question/export")
# async def get_question_export(
#     request: Request,
#     db: Session = Depends(get_db),
#     user: User=Depends(get_current_tutor)
# ):
#     """ 
#     Експорт відфільтрованих питань. 
#     """
#     questions = get_filtered_questions(db, request)
#     if len(questions) == 0:
#         return HTTPException(400, "No questions to export")
#     content = "\n\n".join(str(q) for q in questions)
    
#     fname = f"{questions[0].attr[0:3]}_{len(questions)}.txt"
#     return Response(
#         content=content,
#         media_type="text/plain",
#         headers={"Content-Disposition": f"attachment; filename=\"{fname}\""}
#     )

