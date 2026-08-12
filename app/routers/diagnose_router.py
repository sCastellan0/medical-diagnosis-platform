from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def diagnose_root():
    return {"message": "Diagnosis endpoint ready"}
