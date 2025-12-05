import re
from urllib.parse import quote, unquote
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.user_models import User

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

USER_FILTER = "TUTOR_user_filter"

"""
  {# ------------ User filter form -------------- #} 
  <form action="/filter/user" method="post" class="inline">
      <input name="filter_value" style=" width: 200px;" title="User filter" value="{{filter_val}}">        
      <button type="submit"  title="User filter">Filter</button>

      <input type="hidden" name="referer" value="{{request.url.path}}" > 
      <a href="https://regex101.com/" style="color: gray;">regex</a>  
  </form>

"""
  
@router.post("/user")
async def post_filter_user(
    request: Request,
    filter_value: str = Form(...),
    referer: str = Form(...),
):
    """
    Встановлює кукі з фільтром.
    """
    response = RedirectResponse(referer, status_code=302)  
    set_filter(response, USER_FILTER, filter_value)  
    return response

#--------------------------------- aux 
def set_filter(response, key, value, secure=False):
    if value == '':
        response.delete_cookie(key=key)
    else:
        response.set_cookie(
            key=key,
            value=quote(value),
            max_age=60 * 60 * 24 * 365,
            samesite="lax",
            httponly=False,
            path="/",
            secure=secure,
        )

def get_filter(request, key):
   return unquote(request.cookies.get(key, ""))

#------------------------------------ export utils

def get_user_filter(request):
    return get_filter(request, USER_FILTER)


