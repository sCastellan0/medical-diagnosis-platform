from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.main import get_db
from app.models import DICOMFile

router = APIRouter()

@router.get("/list")
def list_dicoms(db: Session = Depends(get_db)):
    dicoms = db.query(DICOMFile).all()
    return dicoms

@router.get("/{dicom_id}")
def get_dicom_by_id(dicom_id: int, db: Session = Depends(get_db)):
    dicom = db.query(DICOMFile).filter(DICOMFile.id == dicom_id).first()

    if not dicom:
        return {"error": "DICOM no encontrado"}

    return {
        "id": dicom.id,
        "filename": dicom.filename,
        "filepath": dicom.filepath,
        "modality": dicom.modality,
        "patient_name": dicom.patient_name,
        "study_date": dicom.study_date,
        "uploaded_at": dicom.uploaded_at
    }
