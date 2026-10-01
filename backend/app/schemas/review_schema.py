from pydantic import BaseModel
from typing import Dict, Any, Optional, Union
from app.schemas.invoice_schema import InvoiceSchema

class ReviewSubmitRequest(BaseModel):
    reviewer_name: str = "auditor"
    corrected_data: Union[InvoiceSchema, Dict[str, Any]]
    comments: Optional[str] = None

class ReviewSubmitResponse(BaseModel):
    document_id: str
    invoice_id: Optional[int] = None
    status: str
    message: str
    diff_count: int
    diffs: Dict[str, Any]

