from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DICOMFile(Base):
    __tablename__ = "DICOMFiles"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    modality = Column(String(50))
    patient_name = Column(String(255))
    study_date = Column(Date)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
