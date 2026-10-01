from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    query: str = Field(..., description="User question about financial invoices or terms")
    session_id: Optional[str] = Field("default_session", description="Chat conversation session ID")

class SourceCitation(BaseModel):
    source_type: str = Field(..., description="'database_record' or 'vector_document'")
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    snippet: Optional[str] = None
    document_id: Optional[str] = None
    score: Optional[float] = None

class ChatResponse(BaseModel):
    query: str
    query_type: str = Field(..., description="'STRUCTURED_SQL_TOOL' or 'VECTOR_RAG' or 'HYBRID'")
    tool_called: Optional[str] = None
    answer: str
    citations: List[SourceCitation] = Field(default_factory=list)
    raw_data: Optional[Any] = None
