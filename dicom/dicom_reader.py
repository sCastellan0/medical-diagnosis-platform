import pydicom
import numpy as np
from pydicom.pixel_data_handlers.util import apply_voi_lut

class DICOMReader:
    def __init__(self):
        pass

    def load_dicom(self, file_path: str):
        """
        Carga un archivo DICOM desde la ruta indicada.
        """
        ds = pydicom.dcmread(file_path)
        return ds

    def extract_metadata(self, ds):
        """
        Extrae metadatos relevantes del DICOM.
        """
        metadata = {
            "PatientID": getattr(ds, "PatientID", None),
            "StudyDate": getattr(ds, "StudyDate", None),
            "Modality": getattr(ds, "Modality", None),
            "BodyPartExamined": getattr(ds, "BodyPartExamined", None),
            "Rows": getattr(ds, "Rows", None),
            "Columns": getattr(ds, "Columns", None),
        }
        return metadata

    def get_pixel_array(self, ds):
        """
        Convierte el DICOM en un array NumPy listo para modelos.
        Aplica VOI LUT si es necesario.
        """
        try:
            pixel_array = apply_voi_lut(ds.pixel_array, ds)
        except Exception:
            pixel_array = ds.pixel_array

        # Normalizar a rango 0–255
        pixel_array = pixel_array.astype(np.float32)
        pixel_array -= pixel_array.min()
        pixel_array /= pixel_array.max()
        pixel_array *= 255.0

        return pixel_array.astype(np.uint8)
