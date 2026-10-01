import sys
from pathlib import Path

# Add backend directory
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.schemas.invoice_schema import InvoiceSchema, InvoiceItemSchema
from app.utils.gst_validator import (
    validate_gstin_checksum,
    validate_gst_invoice,
    validate_tax_slab,
    validate_hsn_code
)
from app.utils.confidence_engine import calculate_composite_confidence, should_auto_approve

def test_gstin_checksum():
    print("[TEST 1] Testing MOD-36 GSTIN Checksum...")
    # Valid Delhi GSTIN (checksum is 4)
    valid, msg = validate_gstin_checksum("07AAAAA0000A1Z4")
    assert valid, f"Expected 07AAAAA0000A1Z4 to be valid, got: {msg}"

    # Invalid check character (mutated 4 -> 9)
    invalid, err_msg = validate_gstin_checksum("07AAAAA0000A1Z9")
    assert not invalid, "Expected mutated GSTIN to fail checksum"
    print("  -> Passed! Valid GSTIN accepted, mutated checksum rejected.")

def test_intra_state_rules():
    print("[TEST 2] Testing Intra-State Tax Logic (Delhi -> Delhi)...")
    inv = InvoiceSchema(
        invoice_number="INV-001",
        invoice_date="2026-03-01",
        vendor_name="Delhi Supplier Corp",
        vendor_gstin="07AAAAA0000A1Z4",
        customer_name="Delhi Buyer Corp",
        customer_gstin="07BBBBB1111B1ZP",
        place_of_supply="07-Delhi",
        subtotal_amount=10000.0,
        cgst_amount=900.0,
        sgst_amount=900.0,
        igst_amount=0.0,
        total_tax_amount=1800.0,
        grand_total=11800.0,
        is_interstate=False
    )
    report = validate_gst_invoice(inv)
    assert report.is_valid, f"Expected intra-state invoice to be valid. Errors: {report.hard_errors}"

    # Now tamper: make CGST != SGST
    inv_tampered = inv.model_copy()
    inv_tampered.cgst_amount = 900.0
    inv_tampered.sgst_amount = 950.0  # Mismatch!
    report_tampered = validate_gst_invoice(inv_tampered)
    assert not report_tampered.is_valid, "Expected CGST != SGST to fail validation"
    assert any("must equal SGST" in err for err in report_tampered.hard_errors)
    print("  -> Passed! CGST == SGST enforced and mismatch caught.")

def test_inter_state_rules():
    print("[TEST 3] Testing Inter-State Tax Logic (Delhi -> Karnataka)...")
    inv = InvoiceSchema(
        invoice_number="INV-002",
        invoice_date="2026-03-01",
        vendor_name="Delhi Supplier Corp",
        vendor_gstin="07AAAAA0000A1Z4",
        customer_name="Bengaluru Tech Corp",
        customer_gstin="29CCCCC2222C1Z4",
        place_of_supply="29-Karnataka",
        subtotal_amount=20000.0,
        cgst_amount=0.0,
        sgst_amount=0.0,
        igst_amount=3600.0,
        total_tax_amount=3600.0,
        grand_total=23600.0,
        is_interstate=True
    )
    report = validate_gst_invoice(inv)
    assert report.is_valid, f"Expected inter-state invoice to be valid. Errors: {report.hard_errors}"

    # Tamper: charge CGST instead of IGST on inter-state
    inv_tampered = inv.model_copy()
    inv_tampered.cgst_amount = 1800.0
    inv_tampered.sgst_amount = 1800.0
    inv_tampered.igst_amount = 0.0
    report_tampered = validate_gst_invoice(inv_tampered)
    assert not report_tampered.is_valid, "Expected CGST charged on inter-state to fail"
    print("  -> Passed! Inter-state IGST requirement strictly enforced.")

def test_confidence_veto():
    print("[TEST 4] Testing Calibrated Confidence Hard Veto...")
    inv_bad = InvoiceSchema(
        invoice_number="INV-003",
        invoice_date="2026-03-01",
        vendor_name="Supplier Corp",
        vendor_gstin="07AAAAA0000A1Z9",  # Bad checksum
        customer_name="Buyer Corp",
        subtotal_amount=10000.0,
        total_tax_amount=1800.0,
        grand_total=15000.0  # Math mismatch
    )
    report = validate_gst_invoice(inv_bad)
    # Even if LLM claimed 0.99 confidence
    score = calculate_composite_confidence(inv_bad, report, llm_reported_confidence=0.99)
    assert score <= 0.60, f"Expected hard veto to cap score <= 0.60, got {score}"
    assert not should_auto_approve(score, report), "Must not auto-approve bad invoice"
    print(f"  -> Passed! LLM claimed 0.99 confidence, but Calibrated Score was capped at {score} with auto-approval blocked.")

if __name__ == "__main__":
    test_gstin_checksum()
    test_intra_state_rules()
    test_inter_state_rules()
    test_confidence_veto()
    print("\nALL GST ENGINE TESTS PASSED SUCCESSFULLY! (4/4)")
