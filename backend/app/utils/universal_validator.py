import logging
from typing import Dict, Any, List, Tuple
from app.schemas.universal_schema import UniversalDocumentSchema, UniversalValidationReport
from app.schemas.invoice_schema import InvoiceSchema, ValidationReport
from app.utils.gst_validator import validate_gst_invoice
from app.utils.confidence_engine import calculate_composite_confidence, should_auto_approve

logger = logging.getLogger(__name__)

def validate_universal_document(
    doc_dict: Dict[str, Any],
    llm_confidence: float = 0.90
) -> Tuple[UniversalValidationReport, float, bool, List[str]]:
    """
    Validates any document type:
    - If INVOICE: Runs full Indian GST compliance & line-item math checks.
    - If RESUME, MEDICAL_REPORT, LEGAL_CONTRACT, or GENERAL_DOCUMENT: Evaluates field completeness, consistency, and structure.
    
    Returns: (validation_report, composite_confidence, should_auto_approve, flagged_reasons)
    """
    doc_type = str(doc_dict.get("document_type", "GENERAL_DOCUMENT")).strip().upper()
    hard_errors: List[str] = []
    warnings: List[str] = []
    
    # Check if this document is an Invoice
    is_invoice = (
        doc_type in ["INVOICE", "RECEIPT", "BILL", "TAX_INVOICE"] or
        (doc_type == "GENERAL_DOCUMENT" and ("vendor_gstin" in doc_dict or "invoice_number" in doc_dict))
    )

    if is_invoice:
        # Normalize into InvoiceSchema format
        inv_payload = doc_dict.get("invoice_data") if isinstance(doc_dict.get("invoice_data"), dict) else doc_dict
        try:
            inv_schema = InvoiceSchema(**inv_payload)
            gst_report = validate_gst_invoice(inv_schema)
            comp_score = calculate_composite_confidence(
                invoice=inv_schema,
                validation_report=gst_report,
                llm_reported_confidence=llm_confidence
            )
            gst_report.composite_confidence = comp_score
            auto_app = should_auto_approve(comp_score, gst_report)
            flags = list(gst_report.hard_errors) + list(gst_report.warnings)
            
            univ_report = UniversalValidationReport(
                is_valid=gst_report.is_valid,
                hard_errors=gst_report.hard_errors,
                warnings=gst_report.warnings,
                completeness_score=gst_report.rule_score,
                composite_confidence=comp_score
            )
            return univ_report, comp_score, auto_app, flags
        except Exception as e:
            logger.warning(f"Could not strictly validate as GST invoice: {e}. Falling back to universal checks.")

    # Universal Document Validation Rules
    title = doc_dict.get("document_title") or doc_dict.get("title", "")
    summary = doc_dict.get("summary", "")
    primary_entity = doc_dict.get("primary_entity", "")
    key_fields = doc_dict.get("key_fields", {})
    tables = doc_dict.get("tables", [])

    coverage_points = 0.0
    total_points = 4.0

    if title and len(str(title).strip()) > 2:
        coverage_points += 1.0
    else:
        warnings.append("Document title is missing or uninformative")

    if primary_entity and len(str(primary_entity).strip()) > 2:
        coverage_points += 1.0
    else:
        warnings.append("Primary entity (author, vendor, patient, candidate, or organization) could not be identified")

    if summary and len(str(summary).strip()) > 15:
        coverage_points += 1.0
    else:
        warnings.append("Document summary is brief or missing")

    if key_fields and isinstance(key_fields, dict) and len(key_fields) >= 2:
        coverage_points += 1.0
    else:
        warnings.append("Low structured key-value attribute density extracted")

    completeness = coverage_points / total_points

    # Domain-specific soft checks
    if doc_type == "RESUME":
        skills = key_fields.get("skills") or key_fields.get("technical_skills")
        if not skills:
            warnings.append("No technical or domain skills detected in resume")
    elif doc_type == "MEDICAL_REPORT":
        diag = key_fields.get("diagnosis") or key_fields.get("findings") or key_fields.get("prescriptions")
        if not diag:
            warnings.append("No clinical diagnosis or findings detected in medical report")
    elif doc_type == "LEGAL_CONTRACT":
        parties = key_fields.get("parties") or doc_dict.get("secondary_entity")
        if not parties:
            warnings.append("Contract counterparties could not be fully resolved")

    # Composite Confidence: 60% Extraction Completeness + 40% Model Confidence
    composite_confidence = round((0.60 * completeness) + (0.40 * float(llm_confidence or 0.90)), 4)
    
    # Auto-approval: If high completeness (>= 0.75) and composite >= 0.85 and no critical errors
    auto_approve = (completeness >= 0.75 and composite_confidence >= 0.85 and len(hard_errors) == 0)

    report = UniversalValidationReport(
        is_valid=(len(hard_errors) == 0),
        hard_errors=hard_errors,
        warnings=warnings,
        completeness_score=completeness,
        composite_confidence=composite_confidence
    )
    all_flags = list(hard_errors) + list(warnings)
    return report, composite_confidence, auto_approve, all_flags
