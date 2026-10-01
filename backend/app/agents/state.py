from typing import TypedDict, Optional, List, Dict, Any
from app.schemas.invoice_schema import InvoiceSchema, ValidationReport

class InvoiceAgentState(TypedDict):
    document_id: str
    file_bytes: bytes
    mime_type: str
    filename: str
    file_hash: str
    file_size_bytes: int
    
    # Provider & Retry
    llm_provider_name: str
    retry_count: int
    is_duplicate: bool
    duplicate_info: Optional[Dict[str, Any]]
    
    # Extraction & Validation
    raw_model_confidence: Optional[float]
    extracted_data: Optional[Dict[str, Any]]
    validation_report: Optional[Dict[str, Any]]
    composite_confidence: float
    should_auto_approve: bool
    
    # Terminal outcomes
    status: str  # 'AUTO_APPROVED', 'PENDING_REVIEW', 'DUPLICATE', 'FAILED'
    flagged_reasons: List[str]
    invoice_db_id: Optional[int]
