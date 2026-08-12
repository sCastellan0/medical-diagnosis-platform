from fastapi import FastAPI
from app.routers.upload_router import router as upload_router
from app.routers.classify_router import router as classify_router
from app.routers.diagnose_router import router as diagnose_router

app = FastAPI(
    title="Medical Diagnosis Platform",
    description="API to upload DICOM files, classify anatomy, and generate medical diagnoses.",
    version="1.0.0"
)

# Registrar routers
app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(classify_router, prefix="/classify", tags=["Classification"])
app.include_router(diagnose_router, prefix="/diagnose", tags=["Diagnosis"])

@app.get("/")
def root():
    return {"message": "Medical Diagnosis Platform API is running"}
