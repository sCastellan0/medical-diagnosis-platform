from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.main import get_db
from app.models import DICOMFile
from dicom.dicom_reader import DICOMReader
import os
from PIL import Image
import numpy as np

router = APIRouter()
reader = DICOMReader()

TEMP_VIEW_DIR = "temp_views"
os.makedirs(TEMP_VIEW_DIR, exist_ok=True)

@router.get("/view/{dicom_id}")
def view_dicom(
    dicom_id: int,
    slice: int = Query(None, description="Número de slice a visualizar"),
    db: Session = Depends(get_db)
):
    try:
        dicom = db.query(DICOMFile).filter(DICOMFile.id == dicom_id).first()
        if not dicom:
            return {"error": "DICOM no encontrado"}

        filepath = dicom.filepath

        # 🟩 Caso 1: Estudio reconstruido desde ZIP → archivo .npy
        if filepath.endswith(".npy"):
            volume = np.load(filepath)

            total_slices = volume.shape[0]

            # Slice central si no se especifica
            if slice is None:
                slice = total_slices // 2

            if slice < 0 or slice >= total_slices:
                return {"error": f"Slice fuera de rango (0 - {total_slices - 1})"}

            img = volume[slice]

        else:
            # 🟩 Caso 2: DICOM normal (single-slice o multi-slice real)
            ds = reader.load_dicom(filepath)
            pixel_array = reader.get_pixel_array(ds)

            if pixel_array.ndim == 3:
                total_slices = pixel_array.shape[0]

                if slice is None:
                    slice = total_slices // 2

                if slice < 0 or slice >= total_slices:
                    return {"error": f"Slice fuera de rango (0 - {total_slices - 1})"}

                img = pixel_array[slice]
            else:
                img = pixel_array

        # 🟩 Normalizar imagen
        img = img.astype(np.float32)
        img -= img.min()
        img /= img.max()
        img *= 255
        img = img.astype(np.uint8)

        pil_img = Image.fromarray(img)

        # 🟩 Guardar temporalmente
        temp_path = os.path.join(TEMP_VIEW_DIR, f"{dicom.filename}_slice_{slice}.png")
        pil_img.save(temp_path)

        return FileResponse(temp_path, media_type="image/png")

    except Exception as e:
        print("ERROR VIEW:", e)
        return {"error": str(e)}
