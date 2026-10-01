from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.database import Base

class UniversalRecord(Base):
    """
    Normalized relational attribute store for ANY document type:
    Enables precise SQL queries on custom extracted fields (e.g. skills, diagnosis, terms).
    """
    __tablename__ = "universal_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = Column(String(50), nullable=False, index=True)
    field_category = Column(String(50), nullable=True, index=True)  # e.g. 'Metadata', 'Skill', 'Medical', 'Contract', 'Financial'
    field_key = Column(String(100), nullable=False, index=True)
    field_value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    document = relationship("Document", back_populates="universal_records")
