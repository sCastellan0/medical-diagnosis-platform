
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def classify_root():
    return {"message": "Classification endpoint ready"}
