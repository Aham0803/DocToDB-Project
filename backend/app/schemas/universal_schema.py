from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class TableRowSchema(BaseModel):
    cells: Dict[str, Any] = Field(default_factory=dict, description="Column names and values")

class UniversalTableSchema(BaseModel):
    table_name: str = Field("Table", description="Table title, section, or purpose")
    headers: List[str] = Field(default_factory=list, description="Column headers")
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="List of row objects")

class UniversalDocumentSchema(BaseModel):
    """
    Universal schema capable of representing ANY uploaded document:
    Invoices, Resumes, Medical Reports, Legal Contracts, Utility Bills, ID Cards, etc.
    """
    document_type: str = Field(
        "GENERAL_DOCUMENT",
        description="Classified type: INVOICE, RECEIPT, RESUME, MEDICAL_REPORT, LEGAL_CONTRACT, UTILITY_BILL, ID_CARD, ACADEMIC_TRANSCRIPT, or GENERAL_DOCUMENT"
    )
    document_title: str = Field("Untitled Document", description="Concise title or headline")
    summary: str = Field("", description="2-3 sentence executive summary of the document")
    document_date: Optional[str] = Field(None, description="Primary date of the document (YYYY-MM-DD or formatted)")
    primary_entity: Optional[str] = Field(None, description="Main person, vendor, candidate, doctor, or organization")
    secondary_entity: Optional[str] = Field(None, description="Counterparty, customer, employer, patient, or client")
    identifier_number: Optional[str] = Field(None, description="Reference ID, Invoice #, License #, Roll #, or Policy #")
    
    # Dynamic Key-Value attributes extracted from the document
    key_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary of extracted attributes (e.g. skills, experience, diagnosis, medications, terms, amounts)"
    )
    
    # Any extracted tables, matrices, or line items
    tables: List[UniversalTableSchema] = Field(
        default_factory=list,
        description="Structured tables found in the document"
    )
    
    # Financial details if applicable
    financials: Optional[Dict[str, Any]] = Field(
        None,
        description="Monetary figures: currency, grand_total, subtotal, tax_amount, etc."
    )
    
    # Detailed invoice fields if document_type == 'INVOICE'
    invoice_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Full Indian GST invoice fields if document is an invoice"
    )

class UniversalValidationReport(BaseModel):
    is_valid: bool = True
    hard_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    completeness_score: float = 1.0
    composite_confidence: float = 1.0
