from fastapi import APIRouter, UploadFile, File
import os
from dicom.dicom_reader import DICOMReader

router = APIRouter()
reader = DICOMReader()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_dicom(file: UploadFile = File(...)):
    # Validar extensión
    if not file.filename.lower().endswith(".dcm"):
        return {"error": "El archivo debe ser un DICOM (.dcm)"}

    # Guardar temporalmente
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Procesar DICOM
    ds = reader.load_dicom(file_path)
    metadata = reader.extract_metadata(ds)
    pixel_array = reader.get_pixel_array(ds)

    return {
        "filename": file.filename,
        "metadata": metadata,
        "image_shape": pixel_array.shape,
        "message": "DICOM procesado correctamente"
    }