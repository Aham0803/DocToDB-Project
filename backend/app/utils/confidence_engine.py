from typing import Optional, Dict, Any
from app.schemas.invoice_schema import InvoiceSchema, ValidationReport
from app.config import settings

def calculate_composite_confidence(
    invoice: InvoiceSchema,
    validation_report: ValidationReport,
    llm_reported_confidence: Optional[float] = None,
    dual_pass_agreement: Optional[float] = None
) -> float:
    """
    Computes a calibrated multi-signal confidence score.
    Does NOT blindly trust LLM self-reported score.
    
    Weights:
    - 35% GST Rules Score (GSTIN checksum, state POS consistency)
    - 35% Mathematical Consistency Score (items, taxes, grand total balance)
    - 15% Field Format Validation (valid dates, non-empty identifiers, clean numbers)
    - 15% Model / Consistency Signal (agreement or bounded model signal)
    """
    w_rules = 0.35
    w_math = 0.35
    w_format = 0.15
    w_model = 0.15

    # Rule & Math scores from validator
    s_rules = validation_report.rule_score
    s_math = validation_report.math_score
    s_format = validation_report.format_score

    # Model signal: if dual-pass agreement exists, use it. Otherwise calibrate LLM signal.
    if dual_pass_agreement is not None:
        s_model = max(0.0, min(1.0, float(dual_pass_agreement)))
    elif llm_reported_confidence is not None:
        # Penalize overconfident LLM reports by clamping & blending with baseline
        raw_llm = max(0.0, min(1.0, float(llm_reported_confidence)))
        s_model = 0.5 + 0.5 * raw_llm
    else:
        s_model = 0.85

    composite_score = (
        (w_rules * s_rules) +
        (w_math * s_math) +
        (w_format * s_format) +
        (w_model * s_model)
    )

    # HARD VETO: If any hard validation error exists, cap confidence at 0.60
    # This guarantees that invoices with math mismatches or invalid GSTINs NEVER auto-approve.
    if not validation_report.is_valid or len(validation_report.hard_errors) > 0:
        composite_score = min(composite_score, 0.60)

    # Minor warnings penalty (each warning deducts 0.03 up to max 0.15)
    warning_penalty = min(0.15, len(validation_report.warnings) * 0.03)
    composite_score = max(0.0, composite_score - warning_penalty)

    return round(composite_score, 4)


def should_auto_approve(composite_confidence: float, validation_report: ValidationReport) -> bool:
    """
    Strict Auto-Approval Guard:
    1. Zero hard errors.
    2. Composite confidence >= configured threshold (default 0.88).
    """
    if not validation_report.is_valid:
        return False
    if len(validation_report.hard_errors) > 0:
        return False
    return composite_confidence >= settings.CONFIDENCE_AUTO_APPROVE_THRESHOLD
