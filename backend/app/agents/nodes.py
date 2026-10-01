import logging
from typing import Dict, Any
from app.agents.state import InvoiceAgentState
from app.providers.factory import get_llm_provider
from app.schemas.invoice_schema import InvoiceSchema, ValidationReport
from app.utils.gst_validator import validate_gst_invoice
from app.utils.confidence_engine import calculate_composite_confidence, should_auto_approve
from app.utils.date_parser import parse_date_safe
from app.database import SessionLocal
from app.models.invoice import Invoice, InvoiceItem
from app.models.document import Document
from app.models.universal_record import UniversalRecord
from app.services.rag_service import rag_service
from app.utils.universal_validator import validate_universal_document

logger = logging.getLogger(__name__)

async def deduplication_node(state: InvoiceAgentState) -> Dict[str, Any]:
    """
    Checks if this exact file hash or document has already been ingested.
    """
    file_hash = state["file_hash"]
    db = SessionLocal()
    try:
        existing_doc = db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.status.in_(["AUTO_APPROVED", "MANUALLY_APPROVED"])
        ).first()

        if existing_doc:
            logger.info(f"Duplicate file hash detected: {file_hash} matches doc {existing_doc.id}")
            return {
                "is_duplicate": True,
                "status": "DUPLICATE",
                "flagged_reasons": [f"Exact file already processed previously (Document ID: {existing_doc.id})"],
                "duplicate_info": {"matched_doc_id": existing_doc.id, "original_filename": existing_doc.original_filename}
            }
        return {"is_duplicate": False}
    finally:
        db.close()


async def extractor_node(state: InvoiceAgentState) -> Dict[str, Any]:
    """
    Universal Multimodal Extraction Node:
    Calls LLM provider to auto-classify and extract structured data from ANY document.
    """
    if state.get("is_duplicate"):
        return {}

    provider = get_llm_provider(state.get("llm_provider_name"))
    file_bytes = state["file_bytes"]
    mime_type = state["mime_type"]
    filename = state["filename"]

    try:
        doc_dict, raw_conf = await provider.extract_document(file_bytes, mime_type, filename)
        return {
            "extracted_data": doc_dict,
            "raw_model_confidence": raw_conf
        }
    except Exception as e:
        logger.error(f"Extractor node failed: {e}")
        return {
            "status": "FAILED",
            "flagged_reasons": [f"Extraction failed: {str(e)}"],
            "should_auto_approve": False
        }


async def validator_node(state: InvoiceAgentState) -> Dict[str, Any]:
    """
    Universal Validation Node:
    - Runs Indian GST compliance, checksums, and math checks if document is an invoice.
    - Evaluates structural completeness and integrity for all other document types.
    """
    if state.get("is_duplicate") or not state.get("extracted_data"):
        return {}

    data_dict = state["extracted_data"]
    raw_conf = state.get("raw_model_confidence", 0.90)

    report, composite_score, auto_approve, all_flags = validate_universal_document(
        doc_dict=data_dict,
        llm_confidence=raw_conf
    )

    return {
        "validation_report": report.model_dump(),
        "composite_confidence": composite_score,
        "should_auto_approve": auto_approve,
        "flagged_reasons": all_flags
    }



async def refinement_node(state: InvoiceAgentState) -> Dict[str, Any]:
    """
    Self-Correction Retry Loop:
    Provides validation errors back to LLM to re-inspect and fix errors.
    """
    provider = get_llm_provider(state.get("llm_provider_name"))
    file_bytes = state["file_bytes"]
    mime_type = state["mime_type"]
    previous_data = state["extracted_data"]
    val_report = state.get("validation_report", {})
    hard_errors = val_report.get("hard_errors", ["General validation mismatch"])

    doc_type = str((previous_data or {}).get("document_type", "GENERAL_DOCUMENT")).strip().upper()
    if doc_type not in ["INVOICE", "RECEIPT", "BILL", "TAX_INVOICE"]:
        return {"retry_count": state.get("retry_count", 0) + 1}

    logger.info(f"Triggering Self-Correction Retry for Doc {state['document_id']}. Errors: {hard_errors}")

    try:
        refined_invoice, raw_conf = await provider.refine_extraction(
            file_bytes=file_bytes,
            mime_type=mime_type,
            previous_data=previous_data,
            validation_errors=hard_errors
        )
        return {
            "extracted_data": refined_invoice.model_dump(),
            "raw_model_confidence": raw_conf,
            "retry_count": state.get("retry_count", 0) + 1
        }
    except Exception as e:
        logger.error(f"Refinement node failed: {e}")
        return {
            "retry_count": state.get("retry_count", 0) + 1
        }


async def storage_node(state: InvoiceAgentState) -> Dict[str, Any]:
    """
    Final Persistence Node:
    - If AUTO_APPROVED: Inserts into MySQL `invoices` & `invoice_items` and indexes into ChromaDB.
    - If PENDING_REVIEW: Updates document queue record with flags for human inspection.
    """
    db = SessionLocal()
    doc_id = state["document_id"]
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            doc = Document(
                id=doc_id,
                original_filename=state["filename"],
                stored_filepath=f"uploads/{state['filename']}",
                file_hash=state["file_hash"],
                file_type=state["mime_type"],
                file_size_bytes=state["file_size_bytes"],
                llm_provider=state.get("llm_provider_name", "gemini")
            )
            db.add(doc)

        # Handle Duplicate
        if state.get("is_duplicate"):
            doc.status = "DUPLICATE"
            doc.flagged_reasons = state.get("flagged_reasons", [])
            dup_info = state.get("duplicate_info") or {}
            matched_id = dup_info.get("matched_doc_id")
            if matched_id:
                orig = db.query(Document).filter(Document.id == matched_id).first()
                if orig:
                    doc.document_type = orig.document_type
                    doc.document_title = orig.document_title
                    doc.primary_entity = orig.primary_entity
                    doc.summary = orig.summary
                    doc.composite_confidence = orig.composite_confidence
                    doc.extracted_json = orig.extracted_json
            db.commit()
            return {"status": "DUPLICATE"}

        # Check invoice uniqueness on (vendor_gstin, invoice_number, invoice_date) if invoice
        data = state.get("extracted_data") or {}
        inv_data = data.get("invoice_data") if isinstance(data.get("invoice_data"), dict) else data
        v_gstin = str(inv_data.get("vendor_gstin", "")).strip().upper()
        inv_no = str(inv_data.get("invoice_number", "")).strip()
        inv_date = parse_date_safe(inv_data.get("invoice_date", ""))

        if v_gstin and inv_no:
            existing_inv = db.query(Invoice).filter(
                Invoice.vendor_gstin == v_gstin,
                Invoice.invoice_number == inv_no,
                Invoice.invoice_date == inv_date
            ).first()

            if existing_inv:
                logger.info(f"Duplicate invoice record: Vendor {v_gstin}, Inv #{inv_no}, Date {inv_date}")
                doc.status = "DUPLICATE"
                doc.flagged_reasons = [f"Invoice {inv_no} from GSTIN {v_gstin} on {inv_date} already exists in database (Invoice ID: {existing_inv.id})."]
                doc.extracted_json = data
                doc.composite_confidence = state.get("composite_confidence", 0.0)
                db.commit()
                return {"status": "DUPLICATE"}

        # Update Document record with Universal metadata
        doc_type = str(data.get("document_type", "GENERAL_DOCUMENT")).strip().upper()
        doc.document_type = doc_type
        doc.document_title = data.get("document_title") or data.get("title", state["filename"])
        doc.primary_entity = data.get("primary_entity") or inv_data.get("vendor_name") or data.get("candidate_name")
        doc.summary = data.get("summary", "")
        doc.composite_confidence = state.get("composite_confidence", 0.0)
        doc.retry_count = state.get("retry_count", 0)
        doc.flagged_reasons = state.get("flagged_reasons", [])
        doc.extracted_json = data

        # Insert key-value attributes into universal_records table
        key_fields = data.get("key_fields", {})
        if isinstance(key_fields, dict):
            import json
            for k, v in key_fields.items():
                val_str = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                rec = UniversalRecord(
                    document_id=doc_id,
                    document_type=doc_type,
                    field_category="Attribute",
                    field_key=str(k)[:100],
                    field_value=val_str
                )
                db.add(rec)

        if state.get("should_auto_approve") and data:
            invoice_record_id = None
            # If document has invoice details, insert into relational Invoices table
            if inv_no and v_gstin and inv_data.get("grand_total") is not None:
                invoice_record = Invoice(
                    document_id=doc_id,
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
                    verification_type="AUTO",
                    confidence_score=state.get("composite_confidence", 0.90)
                )
                db.add(invoice_record)
                db.flush()
                invoice_record_id = invoice_record.id

                # Insert line items if present
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

            doc.status = "AUTO_APPROVED"
            db.commit()

            # Index into ChromaDB for Semantic Search in background thread
            import threading
            threading.Thread(target=rag_service.index_invoice, args=(doc_id, data), daemon=True).start()

            return {
                "status": "AUTO_APPROVED",
                "invoice_db_id": invoice_record_id
            }
        else:
            # Route to Human Review Queue
            doc.status = "PENDING_REVIEW"
            db.commit()
            return {
                "status": "PENDING_REVIEW"
            }
    except Exception as e:
        db.rollback()
        logger.error(f"Storage node database error: {e}")
        doc.status = "PENDING_REVIEW"
        doc.flagged_reasons = state.get("flagged_reasons", []) + [f"DB storage error: {str(e)}"]
        db.commit()
        return {"status": "PENDING_REVIEW"}
    finally:
        db.close()

