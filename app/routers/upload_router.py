from fastapi import APIRouter, UploadFile, File, Depends
import os
from sqlalchemy.orm import Session
from dicom.dicom_reader import DICOMReader
from app.main import get_db
from app.models import DICOMFile
from datetime import datetime

router = APIRouter()
reader = DICOMReader()

UPLOAD_DIR = "data/dicom_raw"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_dicom(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validar extensión
    if not file.filename.lower().endswith(".dcm"):
        return {"error": "El archivo debe ser un DICOM (.dcm)"}

    # Guardar archivo en carpeta local
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Procesar DICOM
    ds = reader.load_dicom(file_path)
    metadata = reader.extract_metadata(ds)
    pixel_array = reader.get_pixel_array(ds)

    # Insertar metadata en SQL Server
    dicom_record = DICOMFile(
        filename=file.filename,
        filepath=file_path,
        modality=metadata.get("Modality", "Unknown"),
        patient_name=metadata.get("PatientName", "Unknown"),
        study_date=metadata.get("StudyDate", datetime.now().date())
    )

    db.add(dicom_record)
    db.commit()
    db.refresh(dicom_record)

    return {
        "id": dicom_record.id,
        "filename": file.filename,
        "metadata": metadata,
        "image_shape": pixel_array.shape,
        "message": "DICOM procesado y guardado correctamente"
    }
