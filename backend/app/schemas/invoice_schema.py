from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class InvoiceItemSchema(BaseModel):
    item_index: int = 1
    description: str = Field(..., description="Description or name of item/service")
    hsn_sac_code: Optional[str] = Field(None, description="HSN or SAC code (e.g., 998311, 8471)")
    quantity: float = Field(1.0, description="Quantity")
    unit_of_measure: Optional[str] = Field("NOS", description="Unit (e.g., NOS, PCS, KG, HRS)")
    unit_price: float = Field(0.0, description="Unit price / rate")
    taxable_value: float = Field(0.0, description="Taxable amount before tax")
    tax_rate: float = Field(0.0, description="Total GST percentage (e.g., 18.0)")
    cgst_rate: float = Field(0.0, description="CGST percentage (e.g., 9.0)")
    cgst_amount: float = Field(0.0, description="CGST amount in currency")
    sgst_rate: float = Field(0.0, description="SGST percentage (e.g., 9.0)")
    sgst_amount: float = Field(0.0, description="SGST amount in currency")
    igst_rate: float = Field(0.0, description="IGST percentage (e.g., 18.0)")
    igst_amount: float = Field(0.0, description="IGST amount in currency")
    total_amount: float = Field(0.0, description="Total line item amount including taxes")

class InvoiceSchema(BaseModel):
    invoice_number: str = Field(..., description="Invoice / Bill number")
    invoice_date: str = Field(..., description="Date of invoice formatted as YYYY-MM-DD")
    due_date: Optional[str] = Field(None, description="Due date formatted as YYYY-MM-DD")
    currency: str = Field("INR", description="Currency symbol or code, e.g. INR")
    purchase_order_number: Optional[str] = Field(None, description="PO Number if present")
    
    # Vendor / Supplier
    vendor_name: str = Field(..., description="Supplier / Seller legal or trade name")
    vendor_gstin: str = Field(..., description="15-character GSTIN of the vendor")
    vendor_address: Optional[str] = Field(None, description="Vendor complete address")
    vendor_phone: Optional[str] = Field(None, description="Vendor contact phone")
    vendor_email: Optional[str] = Field(None, description="Vendor email address")
    vendor_pan: Optional[str] = Field(None, description="10-digit PAN of vendor (chars 3 to 12 of GSTIN)")
    
    # Customer / Buyer
    customer_name: str = Field(..., description="Buyer / Customer legal or trade name")
    customer_gstin: Optional[str] = Field(None, description="15-character GSTIN of customer if B2B")
    place_of_supply: Optional[str] = Field(None, description="Place of Supply state or state code (POS)")
    customer_address: Optional[str] = Field(None, description="Buyer address")
    
    # Financial Totals
    subtotal_amount: float = Field(0.0, description="Total taxable value before GST")
    cgst_amount: float = Field(0.0, description="Total Central GST amount")
    sgst_amount: float = Field(0.0, description="Total State GST amount")
    igst_amount: float = Field(0.0, description="Total Integrated GST amount")
    total_tax_amount: float = Field(0.0, description="Sum of all GST taxes")
    discount_amount: float = Field(0.0, description="Discount amount applied")
    shipping_amount: float = Field(0.0, description="Shipping or freight charges")
    round_off_amount: float = Field(0.0, description="Round off adjustment amount (+ or -)")
    grand_total: float = Field(..., description="Final invoice payable amount")
    
    # GST Logic
    is_interstate: bool = Field(False, description="True if transaction is inter-state (IGST)")
    reverse_charge: bool = Field(False, description="Whether reverse charge is applicable (Y/N)")
    
    # Bank & Payment
    bank_name: Optional[str] = Field(None, description="Bank Name for payment")
    account_number: Optional[str] = Field(None, description="Account Number")
    ifsc_code: Optional[str] = Field(None, description="Bank IFSC code")
    payment_terms: Optional[str] = Field(None, description="Terms of payment / notes")
    
    # Line items
    items: List[InvoiceItemSchema] = Field(default_factory=list, description="Extracted line items")

class ValidationReport(BaseModel):
    is_valid: bool
    hard_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    rule_score: float = 1.0
    math_score: float = 1.0
    format_score: float = 1.0
    composite_confidence: float = 1.0
    details: Dict[str, Any] = Field(default_factory=dict)
