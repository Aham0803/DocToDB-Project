import re
from typing import Dict, Any, List, Tuple
from app.schemas.invoice_schema import InvoiceSchema, ValidationReport

# Indian GST State / Union Territory Codes
GST_STATE_CODES = {
    "01": "Jammu & Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "25": "Daman & Diu",
    "26": "Dadra & Nagar Haveli",
    "27": "Maharashtra",
    "28": "Andhra Pradesh (Old)",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman & Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh (New)",
    "38": "Ladakh",
    "97": "Other Territory",
    "99": "Centre Jurisdiction",
}

# Standard GST Tax Slabs in India
VALID_GST_SLABS = [0.0, 0.1, 0.25, 1.5, 3.0, 5.0, 12.0, 18.0, 28.0]

# GSTIN MOD-36 Character Mapping
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CHAR_TO_VAL = {c: i for i, c in enumerate(CHARS)}
VAL_TO_CHAR = {i: c for i, c in enumerate(CHARS)}


def validate_gstin_checksum(gstin: str) -> Tuple[bool, str]:
    """
    Validates a 15-character GSTIN format and its official MOD-36 check digit.
    Returns (is_valid, error_message).
    """
    if not gstin or not isinstance(gstin, str):
        return False, "GSTIN is missing or empty"
    
    clean_gstin = gstin.strip().upper()
    if len(clean_gstin) != 15:
        return False, f"GSTIN '{clean_gstin}' length is {len(clean_gstin)}; must be exactly 15 characters"

    pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    if not re.match(pattern, clean_gstin):
        return False, f"GSTIN '{clean_gstin}' does not match standard 15-character pattern (e.g., 07AAAAA0000A1Z5)"

    state_code = clean_gstin[:2]
    if state_code not in GST_STATE_CODES:
        return False, f"State code '{state_code}' in GSTIN '{clean_gstin}' is invalid under Indian GST law"

    # MOD-36 Check Digit Algorithm
    try:
        total_sum = 0
        for i in range(14):
            factor = 1 if (i % 2 == 0) else 2
            val = CHAR_TO_VAL[clean_gstin[i]]
            product = val * factor
            quotient = product // 36
            remainder = product % 36
            total_sum += quotient + remainder

        remainder_sum = total_sum % 36
        check_val = (36 - remainder_sum) % 36
        expected_char = VAL_TO_CHAR[check_val]
        actual_char = clean_gstin[14]

        if expected_char != actual_char:
            return False, f"GSTIN '{clean_gstin}' check character mismatch: expected '{expected_char}', found '{actual_char}'"

        return True, "Valid GSTIN"
    except Exception as e:
        return False, f"Checksum verification error: {str(e)}"


def validate_hsn_code(code: str) -> Tuple[bool, str]:
    """Validate Goods HSN (4, 6, 8 digits) or Services SAC (6 digits starting with 99)."""
    if not code:
        return True, "HSN/SAC not provided"
    
    clean = re.sub(r"[^0-9]", "", str(code))
    if len(clean) in [4, 6, 8]:
        return True, "Valid HSN/SAC code"
    return False, f"HSN/SAC '{code}' should be 4, 6, or 8 digits"


def validate_tax_slab(tax_rate: float) -> Tuple[bool, str]:
    """Check if tax rate is a recognized Indian GST slab."""
    for slab in VALID_GST_SLABS:
        if abs(tax_rate - slab) <= 0.15:
            return True, f"Valid GST slab {slab}%"
    return False, f"Tax rate {tax_rate}% does not match standard GST slabs (0, 5, 12, 18, 28%)"


def extract_state_code_from_pos(pos: str) -> str:
    """Extract 2-digit state code from place of supply string or name."""
    if not pos:
        return ""
    pos_clean = str(pos).strip()
    # Check if first 2 characters are numbers
    m = re.match(r"^(\d{2})", pos_clean)
    if m and m.group(1) in GST_STATE_CODES:
        return m.group(1)
    
    # Check by state name
    for code, name in GST_STATE_CODES.items():
        if name.lower() in pos_clean.lower() or pos_clean.lower() in name.lower():
            return code
    return ""


def validate_gst_invoice(inv: InvoiceSchema) -> ValidationReport:
    """
    Comprehensive GST domain validation engine:
    1. Vendor GSTIN checksum & state code
    2. Buyer GSTIN (if present)
    3. Intra-state vs Inter-state Place of Supply (POS) tax distribution
    4. Line-item tax slab verification
    5. Mathematical reconciliation (subtotal, taxes, grand total)
    """
    hard_errors: List[str] = []
    warnings: List[str] = []
    details: Dict[str, Any] = {}

    rule_checks_passed = 0
    rule_checks_total = 0

    # 1. Vendor GSTIN Checksum
    rule_checks_total += 1
    v_ok, v_msg = validate_gstin_checksum(inv.vendor_gstin)
    details["vendor_gstin_check"] = {"valid": v_ok, "message": v_msg}
    if not v_ok:
        hard_errors.append(f"Vendor GSTIN Error: {v_msg}")
    else:
        rule_checks_passed += 1

    # Check PAN consistency from GSTIN (chars 3 to 12)
    clean_v_gstin = inv.vendor_gstin.strip().upper() if inv.vendor_gstin else ""
    if len(clean_v_gstin) == 15:
        expected_pan = clean_v_gstin[2:12]
        if inv.vendor_pan:
            clean_pan = inv.vendor_pan.strip().upper()
            if clean_pan != expected_pan:
                warnings.append(f"Vendor PAN '{clean_pan}' does not match characters 3-12 of GSTIN '{expected_pan}'")

    # 2. Customer GSTIN (if present)
    if inv.customer_gstin and inv.customer_gstin.strip():
        rule_checks_total += 1
        c_ok, c_msg = validate_gstin_checksum(inv.customer_gstin)
        details["customer_gstin_check"] = {"valid": c_ok, "message": c_msg}
        if not c_ok:
            warnings.append(f"Customer GSTIN Warning: {c_msg}")
        else:
            rule_checks_passed += 1

    # 3. Intra-State vs Inter-State Logic
    supplier_state = clean_v_gstin[:2] if len(clean_v_gstin) >= 2 else ""
    recipient_state = ""
    
    if inv.customer_gstin and len(inv.customer_gstin.strip()) >= 2:
        recipient_state = inv.customer_gstin.strip()[:2]
    elif inv.place_of_supply:
        recipient_state = extract_state_code_from_pos(inv.place_of_supply)

    details["supplier_state_code"] = supplier_state
    details["recipient_state_code"] = recipient_state

    # Tax Amounts
    cgst = float(inv.cgst_amount or 0.0)
    sgst = float(inv.sgst_amount or 0.0)
    igst = float(inv.igst_amount or 0.0)
    total_tax = float(inv.total_tax_amount or 0.0)

    rule_checks_total += 1
    if supplier_state and recipient_state:
        is_intra = (supplier_state == recipient_state)
        details["detected_supply_type"] = "INTRA_STATE" if is_intra else "INTER_STATE"

        if is_intra:
            # Intra-state: Must have CGST + SGST; IGST must be 0
            if igst > 1.0:
                hard_errors.append(f"Intra-state transaction (Supplier State {supplier_state} == POS {recipient_state}), but IGST of ₹{igst:.2f} is charged. Expected CGST + SGST.")
            elif abs(cgst - sgst) > 0.50:
                hard_errors.append(f"Intra-state CGST (₹{cgst:.2f}) must equal SGST (₹{sgst:.2f}) under GST Section 9.")
            else:
                rule_checks_passed += 1
        else:
            # Inter-state: Must have IGST; CGST and SGST must be 0
            if (cgst > 1.0 or sgst > 1.0):
                hard_errors.append(f"Inter-state transaction (Supplier State {supplier_state} != POS {recipient_state}), but CGST (₹{cgst:.2f}) / SGST (₹{sgst:.2f}) is charged. Expected IGST.")
            else:
                rule_checks_passed += 1
    else:
        # Fallback based on charged taxes if state codes were partially missing
        if igst > 1.0 and (cgst > 1.0 or sgst > 1.0):
            hard_errors.append(f"Ambiguous tax breakup: Both IGST (₹{igst:.2f}) and CGST/SGST (₹{cgst:.2f}/₹{sgst:.2f}) are present on the same invoice.")
        else:
            rule_checks_passed += 1

    # 4. Tax Slabs and HSN on Line Items
    item_checks_passed = 0
    item_checks_total = len(inv.items) if inv.items else 1

    for idx, item in enumerate(inv.items):
        # Tax slab check
        slab_ok, slab_msg = validate_tax_slab(item.tax_rate)
        if not slab_ok and item.tax_rate > 0.0:
            warnings.append(f"Item #{idx+1} ('{item.description[:30]}'): {slab_msg}")
        else:
            item_checks_passed += 1

        # HSN check
        if item.hsn_sac_code:
            hsn_ok, hsn_msg = validate_hsn_code(item.hsn_sac_code)
            if not hsn_ok:
                warnings.append(f"Item #{idx+1}: {hsn_msg}")

    # 5. Mathematical Reconciliation
    math_checks_passed = 0
    math_checks_total = 3

    # Check 1: Sum of line items taxable values vs subtotal
    if inv.items:
        items_taxable_sum = sum(float(i.taxable_value or (i.quantity * i.unit_price)) for i in inv.items)
        if abs(items_taxable_sum - float(inv.subtotal_amount)) <= 1.0:
            math_checks_passed += 1
        else:
            warnings.append(f"Subtotal mismatch: Sum of item taxable values (₹{items_taxable_sum:.2f}) does not match subtotal (₹{inv.subtotal_amount:.2f})")
    else:
        math_checks_passed += 1

    # Check 2: Taxes sum check: (cgst + sgst + igst) vs total_tax_amount
    tax_component_sum = cgst + sgst + igst
    if abs(tax_component_sum - total_tax) <= 1.0:
        math_checks_passed += 1
    else:
        hard_errors.append(f"Tax math mismatch: CGST ({cgst:.2f}) + SGST ({sgst:.2f}) + IGST ({igst:.2f}) = ₹{tax_component_sum:.2f}, but total_tax is ₹{total_tax:.2f}")

    # Check 3: Grand total reconciliation
    subtotal = float(inv.subtotal_amount or 0.0)
    discount = float(inv.discount_amount or 0.0)
    shipping = float(inv.shipping_amount or 0.0)
    round_off = float(inv.round_off_amount or 0.0)
    grand_total = float(inv.grand_total or 0.0)

    calculated_grand_total = (subtotal + total_tax + shipping - discount + round_off)
    diff = abs(calculated_grand_total - grand_total)

    if diff <= 1.50:  # ₹1.50 tolerance for roundoff
        math_checks_passed += 1
    else:
        hard_errors.append(f"Grand Total mismatch: Subtotal ({subtotal:.2f}) + Tax ({total_tax:.2f}) + Shipping ({shipping:.2f}) - Discount ({discount:.2f}) + RoundOff ({round_off:.2f}) = ₹{calculated_grand_total:.2f}, but extracted Grand Total is ₹{grand_total:.2f} (Difference: ₹{diff:.2f})")

    # 6. Format Verification (Dates & Non-Empty Identifiers)
    format_score = 1.0
    if not inv.invoice_number or inv.invoice_number.strip() in ["", "NA", "N/A", "null"]:
        hard_errors.append("Invoice number is empty or missing")
        format_score -= 0.3

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", inv.invoice_date or ""):
        warnings.append(f"Invoice date '{inv.invoice_date}' is not standard YYYY-MM-DD")
        format_score -= 0.2

    # Scores
    rule_score = round(rule_checks_passed / max(rule_checks_total, 1), 4)
    math_score = round(math_checks_passed / max(math_checks_total, 1), 4)
    format_score = max(0.0, round(format_score, 4))

    is_valid = (len(hard_errors) == 0)

    return ValidationReport(
        is_valid=is_valid,
        hard_errors=hard_errors,
        warnings=warnings,
        rule_score=rule_score,
        math_score=math_score,
        format_score=format_score,
        composite_confidence=1.0,  # Will be calculated by confidence engine
        details=details
    )
