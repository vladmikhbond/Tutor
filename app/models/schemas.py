from typing import List
from pydantic import BaseModel


class HelpItem(BaseModel):
    head: str
    body: List[str]
