
from datetime import datetime


from fastapi import Depends

from pydantic import BaseModel
from fastapi import APIRouter
from sqlalchemy.orm import Session

from ..models.attend_models import Snapshot
from ..dal import get_attend_db


API_KEY = "secret123"

router = APIRouter()

from pydantic import BaseModel

class SnapshotRequest(BaseModel):
    username: str
    visitors: list[str]

@router.post("/snapshot")
async def post_snapshot(
    data: SnapshotRequest,
    db: Session = Depends(get_attend_db)
):
    snapshot = Snapshot(
        username=data.username,
        visitors=",".join(data.visitors),  # або json.dumps
        when=datetime.now()
    )
    db.add(snapshot)
    db.commit()
    return {"status": "ok"}
