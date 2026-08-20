from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar la sesión de la base de datos
from app.database import SessionLocal

# Función para obtener la sesión de SQL Server
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear la app FastAPI
app = FastAPI(
    title="Medical Diagnosis Platform",
    description="API to upload DICOM files, classify anatomy, and generate medical diagnoses.",
    version="1.0.0"
)

# Routers
from app.routers.upload_router import router as upload_router
from app.routers.classify_router import router as classify_router
from app.routers.diagnose_router import router as diagnose_router
from app.routers.list_router import router as list_router
from app.routers.download_router import router as download_router
from app.routers.view_router import router as view_router
from app.routers.upload_zip_router import router as upload_zip_router

# Registrar routers
app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(classify_router, prefix="/classify", tags=["Classification"])
app.include_router(diagnose_router, prefix="/diagnose", tags=["Diagnosis"])
app.include_router(list_router, prefix="/dicom", tags=["DICOM"])
app.include_router(download_router, prefix="/dicom", tags=["DICOM"])
app.include_router(view_router, prefix="/dicom", tags=["DICOM"])
app.include_router(upload_zip_router, prefix="/dicom", tags=["DICOM"])

# Ruta raíz
@app.get("/")
def root():
    return {"message": "Medical Diagnosis Platform API is running"}

