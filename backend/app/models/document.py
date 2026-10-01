from datetime import datetime
from sqlalchemy import Column, String, BigInteger, Enum, DECIMAL, Integer, JSON, DateTime, text
from sqlalchemy.orm import relationship
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True)
    original_filename = Column(String(255), nullable=False)
    stored_filepath = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    file_type = Column(String(50), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    status = Column(
        Enum("QUEUED", "PROCESSING", "AUTO_APPROVED", "PENDING_REVIEW", "MANUALLY_APPROVED", "REJECTED", "DUPLICATE", name="document_status"),
        nullable=False,
        default="QUEUED",
        index=True
    )
    document_type = Column(String(50), nullable=False, default="GENERAL_DOCUMENT", index=True)
    document_title = Column(String(255), nullable=True)
    primary_entity = Column(String(255), nullable=True, index=True)
    summary = Column(String(1000), nullable=True)
    composite_confidence = Column(DECIMAL(5, 4), default=0.0000)
    llm_provider = Column(String(50), nullable=False, default="gemini")
    retry_count = Column(Integer, nullable=False, default=0)
    flagged_reasons = Column(JSON, nullable=True)
    extracted_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    invoices = relationship("Invoice", back_populates="document", cascade="all, delete-orphan")
    corrections = relationship("HumanCorrection", back_populates="document", cascade="all, delete-orphan")
    universal_records = relationship("UniversalRecord", back_populates="document", cascade="all, delete-orphan")
