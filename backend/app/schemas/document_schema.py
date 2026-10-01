from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    message: str

class DocumentStatusResponse(BaseModel):
    id: str
    original_filename: str
    stored_filepath: str
    file_type: str
    file_size_bytes: int
    document_type: Optional[str] = "GENERAL_DOCUMENT"
    document_title: Optional[str] = None
    primary_entity: Optional[str] = None
    summary: Optional[str] = None
    status: str
    composite_confidence: float
    llm_provider: str
    retry_count: int
    flagged_reasons: Optional[List[str]] = None
    extracted_json: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentQueueItem(BaseModel):
    id: str
    original_filename: str
    file_type: str
    document_type: Optional[str] = "GENERAL_DOCUMENT"
    document_title: Optional[str] = None
    primary_entity: Optional[str] = None
    status: str
    composite_confidence: float
    retry_count: int
    flagged_reasons: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

