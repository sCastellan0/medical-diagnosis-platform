from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.main import get_db
from app.models import DICOMFile
from dicom.dicom_reader import DICOMReader

import zipfile
import tempfile
import os
import numpy as np

router = APIRouter()
reader = DICOMReader()

@router.post("/upload_zip")
async def upload_dicom_zip(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Crear carpeta temporal
        temp_dir = tempfile.mkdtemp()

        # Guardar ZIP temporalmente
        zip_path = os.path.join(temp_dir, file.filename)
        with open(zip_path, "wb") as f:
            f.write(await file.read())

        # Extraer ZIP
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Buscar todos los .dcm
        dicom_files = []
        for root, _, files in os.walk(temp_dir):
            for name in files:
                if name.lower().endswith(".dcm"):
                    dicom_files.append(os.path.join(root, name))

        if not dicom_files:
            return {"error": "No se encontraron archivos DICOM en el ZIP"}

        # -----------------------------
        # EXTRAER MODALIDAD REAL
        # -----------------------------
        ds_first = reader.load_dicom(dicom_files[0])
        modality_raw = getattr(ds_first, "Modality", None)

        modality_map = {
            "CR": "RX",
            "DX": "RX",
            "CT": "CT",
            "MR": "MRI",
            "PT": "PET",
            "NM": "SPECT"
        }

        modality_human = modality_map.get(modality_raw, modality_raw)

        # -----------------------------
        # LEER SLICES Y ORDENARLOS
        # -----------------------------
        slices = []
        for path in dicom_files:
            ds = reader.load_dicom(path)

            instance = int(getattr(ds, "InstanceNumber", 0))
            pixel = reader.get_pixel_array(ds)

            slices.append((instance, pixel))

        slices.sort(key=lambda x: x[0])

        # -----------------------------
        # RECONSTRUIR VOLUMEN 3D
        # -----------------------------
        volume = np.stack([s[1] for s in slices], axis=0)

        # -----------------------------
        # GUARDAR VOLUMEN COMO .NPY
        # -----------------------------
        os.makedirs("data/dicom_volumes", exist_ok=True)
        save_path = f"data/dicom_volumes/{file.filename.replace('.zip','')}.npy"
        np.save(save_path, volume)

        # -----------------------------
        # GUARDAR METADATA EN SQL SERVER
        # -----------------------------
        dicom_record = DICOMFile(
            filename=file.filename,
            filepath=save_path,
            modality=modality_human,
            patient_name=None,
            study_date=None
        )

        db.add(dicom_record)
        db.commit()
        db.refresh(dicom_record)

        return {
            "message": "Estudio ZIP procesado correctamente",
            "id": dicom_record.id,
            "modality": modality_human,
            "slices": volume.shape[0],
            "shape": volume.shape
        }

    except Exception as e:
        print("ERROR ZIP:", e)
        return {"error": str(e)}
