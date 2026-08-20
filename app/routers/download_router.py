from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.main import get_db
from app.models import DICOMFile

router = APIRouter()

@router.get("/download/{dicom_id}")
def download_dicom(dicom_id: int, db: Session = Depends(get_db)):
    dicom = db.query(DICOMFile).filter(DICOMFile.id == dicom_id).first()

    if not dicom:
        return {"error": "DICOM no encontrado"}

    return FileResponse(
        dicom.filepath,
        media_type="application/dicom",
        filename=dicom.filename
    )
