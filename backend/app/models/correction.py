from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.database import Base

class HumanCorrection(Base):
    __tablename__ = "human_corrections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_name = Column(String(100), nullable=False, default="system_reviewer")
    original_extracted_json = Column(JSON, nullable=False)
    human_corrected_json = Column(JSON, nullable=False)
    field_diffs = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="corrections")
