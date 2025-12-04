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

html_sample_for_user_filter ="""

<form action="/filter/user" method="post" >
    <fieldset role="group" style="margin-top: 16px;">
        <input name="filter_value"  id="u_filter_value" style="height: 10px; width: 200px;" >        
        <input type="hidden" name="referer" id="u_referer">
        <button type="submit" class="small" title="Users">U</button>&nbsp;
        <a href="https://regex101.com/" style="color: gray;">re</a>  
    </fieldset>
</form> 

<script>
    // Встановлює значення в поле фільтру при завантаженні сторінки

    const USER_FILTER = "TUTOR_user_filter"

    u_referer.value = document.location.pathname;

    const userFilterValue = getCookieValue(USER_FILTER)
    if (userFilterValue != undefined){
        u_filter_value.value = userFilterValue
    }
                
    function getCookieValue(key) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${key}=`);
        if (parts.length === 2) {
            let value = parts.pop().split(';').shift();
            value = decodeURIComponent(value);
            return value
        }
    }
</script>

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


def get_filtered_users(db, request):
    """
    Повертає відфільтрованих користувачів.
    """
    users = db.query(User).all()
    filter = unquote(request.cookies.get(USER_FILTER, ""))
     
    if filter:
        users = [u for u in users if re.search(filter, u.username, re.RegexFlag.U) is not None] 
    users.sort(key=lambda u: u.username)
    return users
