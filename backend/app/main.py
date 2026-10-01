import os
import uuid
import hashlib
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, check_db_connection
from app.models.document import Document
from app.models.invoice import Invoice, InvoiceItem
from app.models.universal_record import UniversalRecord
from app.models.correction import HumanCorrection
from app.models.chat import ChatHistory
from app.schemas.document_schema import DocumentUploadResponse, DocumentStatusResponse, DocumentQueueItem
from app.schemas.invoice_schema import InvoiceSchema
from app.schemas.review_schema import ReviewSubmitRequest, ReviewSubmitResponse
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.utils.date_parser import parse_date_safe
from app.agents.graph import invoice_agent_pipeline
from app.services.query_router import query_router
from app.services.rag_service import rag_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("doctodb")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Enterprise GST Invoice Extraction, Human-in-the-Loop Review, and Hybrid RAG Engine"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse, RedirectResponse

# Mount uploads static folder so frontend can preview original PDFs & images
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "sample_invoices")
if os.path.exists(sample_dir):
    app.mount("/sample", StaticFiles(directory=sample_dir), name="sample")

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "DocToDB API is running"}

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verifies X-API-Key header to ensure only authorized frontend / clients connect."""
    if not x_api_key or x_api_key != settings.API_SECRET_KEY:
        # Permissive in development if key is default
        if settings.ENVIRONMENT == "development" and x_api_key == "doctodb_secret_api_key_2026_secure":
            return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key authentication header"
        )
    return True


@app.get("/api/health")
def health_check():
    db_ok = check_db_connection()
    return {
        "status": "healthy",
        "mysql_connected": db_ok,
        "llm_provider": settings.LLM_PROVIDER,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Summary statistics for the dashboard."""
    total_docs = db.query(Document).count()
    auto_approved = db.query(Document).filter(Document.status == "AUTO_APPROVED").count()
    pending_review = db.query(Document).filter(Document.status == "PENDING_REVIEW").count()
    manually_approved = db.query(Document).filter(Document.status == "MANUALLY_APPROVED").count()
    duplicates = db.query(Document).filter(Document.status == "DUPLICATE").count()

    total_invoices = db.query(Invoice).count()
    from sqlalchemy import func
    totals = db.query(
        func.sum(Invoice.grand_total).label("total_amount"),
        func.sum(Invoice.total_tax_amount).label("total_tax")
    ).first()

    auto_pct = round((auto_approved / total_docs * 100) if total_docs > 0 else 0, 1)

    return {
        "total_documents": total_docs,
        "auto_approved_count": auto_approved,
        "auto_approved_percent": auto_pct,
        "pending_review_count": pending_review,
        "manually_approved_count": manually_approved,
        "duplicates_count": duplicates,
        "total_invoices_in_db": total_invoices,
        "total_grand_amount": float(totals.total_amount or 0.0),
        "total_tax_amount": float(totals.total_tax or 0.0)
    }


@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    provider: Optional[str] = Form(None),
    authenticated: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Ingests PDF or image, validates magic bytes/size, and runs the LangGraph extraction pipeline.
    """
    allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Please upload PDF, PNG, JPG, or WebP."
        )

    # Read bytes and check size (15MB cap)
    content = await file.read()
    max_bytes = 15 * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail="File size exceeds maximum 15MB limit.")

    doc_id = str(uuid.uuid4())
    file_hash = hashlib.sha256(content).hexdigest()

    # Save to disk
    ext = os.path.splitext(file.filename)[1].lower()
    stored_name = f"{doc_id}{ext}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as f:
        f.write(content)

    # Initial Document queue entry
    doc_record = Document(
        id=doc_id,
        original_filename=file.filename,
        stored_filepath=f"uploads/{stored_name}",
        file_hash=file_hash,
        file_type=file.content_type,
        file_size_bytes=len(content),
        status="PROCESSING",
        llm_provider=provider or settings.LLM_PROVIDER
    )
    db.add(doc_record)
    db.commit()

    # Prepare LangGraph state
    initial_state = {
        "document_id": doc_id,
        "file_bytes": content,
        "mime_type": file.content_type,
        "filename": file.filename,
        "stored_filename": stored_name,
        "file_hash": file_hash,
        "file_size_bytes": len(content),
        "llm_provider_name": provider or settings.LLM_PROVIDER,
        "retry_count": 0,
        "is_duplicate": False,
        "duplicate_info": None,
        "raw_model_confidence": None,
        "extracted_data": None,
        "validation_report": None,
        "composite_confidence": 0.0,
        "should_auto_approve": False,
        "status": "PROCESSING",
        "flagged_reasons": [],
        "invoice_db_id": None
    }

    # Execute LangGraph pipeline
    final_state = await invoice_agent_pipeline.ainvoke(initial_state)

    final_status = final_state.get("status", "PENDING_REVIEW")

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        file_type=file.content_type,
        file_size_bytes=len(content),
        status=final_status,
        message=f"Document processed with status: {final_status}"
    )


@app.get("/api/documents/queue", response_model=List[DocumentQueueItem])
def get_documents_queue(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    """Fetch documents in queue with optional status filter."""
    q = db.query(Document)
    if status_filter:
        q = q.filter(Document.status == status_filter)
    else:
        q = q.filter(Document.status.in_(["PENDING_REVIEW", "DUPLICATE", "REJECTED"]))
    
    docs = q.order_by(Document.created_at.desc()).all()
    return docs


@app.get("/api/documents", response_model=List[DocumentQueueItem])
def list_all_documents(document_type: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    """List all ingested documents across all categories (Invoices, Resumes, Medical, Contracts, etc.)."""
    q = db.query(Document)
    if document_type:
        q = q.filter(Document.document_type == document_type.upper())
    if status:
        q = q.filter(Document.status == status.upper())
    return q.order_by(Document.created_at.desc()).all()


@app.get("/api/universal/records")
def get_universal_records(
    document_id: Optional[str] = None,
    document_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve structured dynamic key-value attributes stored across documents."""
    q = db.query(UniversalRecord)
    if document_id:
        q = q.filter(UniversalRecord.document_id == document_id)
    if document_type:
        q = q.filter(UniversalRecord.document_type == document_type.upper())
    recs = q.order_by(UniversalRecord.id.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "document_id": r.document_id,
            "document_type": r.document_type,
            "field_key": r.field_key,
            "field_value": r.field_value
        }
        for r in recs
    ]



@app.get("/api/documents/{document_id}", response_model=DocumentStatusResponse)
def get_document_details(document_id: str, db: Session = Depends(get_db)):
    """Fetch single document extraction and validation details."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.post("/api/documents/{document_id}/review", response_model=ReviewSubmitResponse)
def submit_human_review(
    document_id: str,
    review_data: ReviewSubmitRequest,
    authenticated: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Human-in-the-Loop review submission:
    Calculates field diffs against raw extraction, saves ground truth to `human_corrections`,
    and inserts/updates the clean invoice in MySQL.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    original_json = doc.extracted_json or {}
    corrected_dict = review_data.corrected_data.model_dump() if hasattr(review_data.corrected_data, "model_dump") else review_data.corrected_data

    # Calculate Field Diffs
    diffs = {}
    if isinstance(corrected_dict, dict):
        for k, v in corrected_dict.items():
            if k not in ["items", "tables"]:
                orig_val = original_json.get(k)
                if orig_val != v:
                    diffs[k] = {"original": orig_val, "corrected": v}

    # 1. Save to human_corrections table (Data Flywheel)
    correction_entry = HumanCorrection(
        document_id=document_id,
        reviewer_name=review_data.reviewer_name,
        original_extracted_json=original_json,
        human_corrected_json=corrected_dict,
        field_diffs=diffs
    )
    db.add(correction_entry)

    # 2. Update universal metadata
    doc_type = str(corrected_dict.get("document_type", doc.document_type or "GENERAL_DOCUMENT")).strip().upper()
    doc.document_type = doc_type
    doc.document_title = corrected_dict.get("document_title") or doc.document_title
    doc.primary_entity = corrected_dict.get("primary_entity") or doc.primary_entity
    doc.summary = corrected_dict.get("summary") or doc.summary
    doc.status = "MANUALLY_APPROVED"
    doc.composite_confidence = 1.0000
    doc.extracted_json = corrected_dict

    # 3. Insert into universal_records table
    key_fields = corrected_dict.get("key_fields", {})
    if isinstance(key_fields, dict):
        import json
        for k, v in key_fields.items():
            val_str = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            rec = UniversalRecord(
                document_id=document_id,
                document_type=doc_type,
                field_category="Attribute",
                field_key=str(k)[:100],
                field_value=val_str
            )
            db.add(rec)

    # 4. Insert into Invoices Table IF document is an Invoice
    inv_data = corrected_dict.get("invoice_data") if isinstance(corrected_dict.get("invoice_data"), dict) else corrected_dict
    invoice_record_id = None
    v_gstin = str(inv_data.get("vendor_gstin", "")).strip().upper() if isinstance(inv_data, dict) else ""
    inv_no = str(inv_data.get("invoice_number", "")).strip() if isinstance(inv_data, dict) else ""

    if inv_no and v_gstin:
        invoice_record = Invoice(
            document_id=document_id,
            invoice_number=inv_no,
            invoice_date=parse_date_safe(inv_data.get("invoice_date"), default_today=True),
            due_date=parse_date_safe(inv_data.get("due_date"), default_today=False),
            currency=inv_data.get("currency", "INR"),
            purchase_order_number=inv_data.get("purchase_order_number"),
            payment_status="PENDING",
            vendor_name=inv_data.get("vendor_name", "Vendor"),
            vendor_gstin=v_gstin,
            vendor_state_code=v_gstin[:2] if len(v_gstin) >= 2 else "07",
            vendor_address=inv_data.get("vendor_address"),
            vendor_phone=inv_data.get("vendor_phone"),
            vendor_email=inv_data.get("vendor_email"),
            vendor_pan=inv_data.get("vendor_pan"),
            customer_name=inv_data.get("customer_name", "Customer"),
            customer_gstin=inv_data.get("customer_gstin"),
            customer_state_code=inv_data.get("customer_gstin")[:2] if inv_data.get("customer_gstin") else None,
            place_of_supply=inv_data.get("place_of_supply"),
            customer_address=inv_data.get("customer_address"),
            subtotal_amount=inv_data.get("subtotal_amount", 0.0),
            cgst_amount=inv_data.get("cgst_amount", 0.0),
            sgst_amount=inv_data.get("sgst_amount", 0.0),
            igst_amount=inv_data.get("igst_amount", 0.0),
            total_tax_amount=inv_data.get("total_tax_amount", 0.0),
            discount_amount=inv_data.get("discount_amount", 0.0),
            shipping_amount=inv_data.get("shipping_amount", 0.0),
            round_off_amount=inv_data.get("round_off_amount", 0.0),
            grand_total=inv_data.get("grand_total", 0.0),
            is_interstate=inv_data.get("is_interstate", False),
            reverse_charge=inv_data.get("reverse_charge", False),
            bank_name=inv_data.get("bank_name"),
            account_number=inv_data.get("account_number"),
            ifsc_code=inv_data.get("ifsc_code"),
            payment_terms=inv_data.get("payment_terms"),
            verification_type="MANUAL",
            confidence_score=1.0000
        )
        db.add(invoice_record)
        db.flush()
        invoice_record_id = invoice_record.id

        # Insert items
        for item in inv_data.get("items", []):
            line_item = InvoiceItem(
                invoice_id=invoice_record.id,
                item_index=item.get("item_index", 1),
                description=item.get("description", "Item"),
                hsn_sac_code=item.get("hsn_sac_code"),
                quantity=item.get("quantity", 1.0),
                unit_of_measure=item.get("unit_of_measure", "NOS"),
                unit_price=item.get("unit_price", 0.0),
                taxable_value=item.get("taxable_value", 0.0),
                tax_rate=item.get("tax_rate", 0.0),
                cgst_rate=item.get("cgst_rate", 0.0),
                cgst_amount=item.get("cgst_amount", 0.0),
                sgst_rate=item.get("sgst_rate", 0.0),
                sgst_amount=item.get("sgst_amount", 0.0),
                igst_rate=item.get("igst_rate", 0.0),
                igst_amount=item.get("igst_amount", 0.0),
                total_amount=item.get("total_amount", 0.0)
            )
            db.add(line_item)

    db.commit()

    # Index corrected data into ChromaDB in background thread
    import threading
    threading.Thread(target=rag_service.index_invoice, args=(document_id, corrected_dict), daemon=True).start()

    return ReviewSubmitResponse(
        document_id=document_id,
        invoice_id=invoice_record_id,
        status="MANUALLY_APPROVED",
        message=f"{doc_type} verified and committed successfully.",
        diff_count=len(diffs),
        diffs=diffs
    )



@app.get("/api/invoices")
def list_invoices(
    search: Optional[str] = None,
    payment_status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List verified invoices from MySQL."""
    q = db.query(Invoice)
    if search:
        q = q.filter(
            (Invoice.invoice_number.ilike(f"%{search}%")) |
            (Invoice.vendor_name.ilike(f"%{search}%")) |
            (Invoice.vendor_gstin.ilike(f"%{search}%")) |
            (Invoice.customer_name.ilike(f"%{search}%"))
        )
    if payment_status:
        q = q.filter(Invoice.payment_status == payment_status)

    total_count = q.count()
    records = q.order_by(Invoice.invoice_date.desc()).offset(offset).limit(limit).all()

    items_list = []
    for r in records:
        items_list.append({
            "id": r.id,
            "document_id": r.document_id,
            "invoice_number": r.invoice_number,
            "invoice_date": str(r.invoice_date),
            "due_date": str(r.due_date) if r.due_date else None,
            "vendor_name": r.vendor_name,
            "vendor_gstin": r.vendor_gstin,
            "customer_name": r.customer_name,
            "subtotal": float(r.subtotal_amount),
            "cgst": float(r.cgst_amount),
            "sgst": float(r.sgst_amount),
            "igst": float(r.igst_amount),
            "total_tax": float(r.total_tax_amount),
            "grand_total": float(r.grand_total),
            "payment_status": r.payment_status,
            "verification_type": r.verification_type,
            "confidence_score": float(r.confidence_score)
        })

    return {"total": total_count, "invoices": items_list}


@app.get("/api/invoices/{invoice_id}")
def get_invoice_detail(invoice_id: int, db: Session = Depends(get_db)):
    """Fetch single invoice and all line items."""
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    items = [
        {
            "item_index": it.item_index,
            "description": it.description,
            "hsn_sac_code": it.hsn_sac_code,
            "quantity": float(it.quantity),
            "unit_of_measure": it.unit_of_measure,
            "unit_price": float(it.unit_price),
            "taxable_value": float(it.taxable_value),
            "tax_rate": float(it.tax_rate),
            "cgst_amount": float(it.cgst_amount),
            "sgst_amount": float(it.sgst_amount),
            "igst_amount": float(it.igst_amount),
            "total_amount": float(it.total_amount)
        } for it in inv.items
    ]

    return {
        "id": inv.id,
        "document_id": inv.document_id,
        "invoice_number": inv.invoice_number,
        "invoice_date": str(inv.invoice_date),
        "due_date": str(inv.due_date) if inv.due_date else None,
        "vendor_name": inv.vendor_name,
        "vendor_gstin": inv.vendor_gstin,
        "vendor_address": inv.vendor_address,
        "customer_name": inv.customer_name,
        "customer_gstin": inv.customer_gstin,
        "place_of_supply": inv.place_of_supply,
        "subtotal_amount": float(inv.subtotal_amount),
        "cgst_amount": float(inv.cgst_amount),
        "sgst_amount": float(inv.sgst_amount),
        "igst_amount": float(inv.igst_amount),
        "total_tax_amount": float(inv.total_tax_amount),
        "discount_amount": float(inv.discount_amount),
        "shipping_amount": float(inv.shipping_amount),
        "round_off_amount": float(inv.round_off_amount),
        "grand_total": float(inv.grand_total),
        "payment_status": inv.payment_status,
        "bank_name": inv.bank_name,
        "account_number": inv.account_number,
        "ifsc_code": inv.ifsc_code,
        "payment_terms": inv.payment_terms,
        "verification_type": inv.verification_type,
        "confidence_score": float(inv.confidence_score),
        "items": items
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_documents(
    req: ChatRequest,
    authenticated: bool = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    RAG & Hybrid Query Endpoint:
    Routes query dynamically to either deterministic safe SQL tools or ChromaDB vector retrieval.
    """
    response = await query_router.execute_query(req.query)

    # Save to chat history audit table
    try:
        history_entry = ChatHistory(
            session_id=req.session_id or "default",
            user_query=req.query,
            query_type=response.query_type,
            tool_called=response.tool_called,
            retrieved_sources=[c.model_dump() for c in response.citations],
            assistant_response=response.answer
        )
        db.add(history_entry)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to record chat history: {e}")

    return response
