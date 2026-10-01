from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DECIMAL, Boolean, Text, Enum, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import relationship
from app.database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    invoice_number = Column(String(100), nullable=False)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=True)
    currency = Column(String(10), nullable=False, default="INR")
    purchase_order_number = Column(String(100), nullable=True)
    payment_status = Column(
        Enum("PENDING", "PAID", "OVERDUE", "PARTIALLY_PAID", name="payment_status"),
        nullable=False,
        default="PENDING",
        index=True
    )

    # Vendor Details
    vendor_name = Column(String(255), nullable=False, index=True)
    vendor_gstin = Column(String(15), nullable=False, index=True)
    vendor_state_code = Column(String(2), nullable=False)
    vendor_address = Column(Text, nullable=True)
    vendor_phone = Column(String(50), nullable=True)
    vendor_email = Column(String(100), nullable=True)
    vendor_pan = Column(String(10), nullable=True)

    # Customer Details
    customer_name = Column(String(255), nullable=False, index=True)
    customer_gstin = Column(String(15), nullable=True)
    customer_state_code = Column(String(2), nullable=True)
    place_of_supply = Column(String(100), nullable=True)
    customer_address = Column(Text, nullable=True)

    # Financial Totals
    subtotal_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    cgst_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    sgst_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    igst_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    total_tax_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    discount_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    shipping_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    round_off_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    grand_total = Column(DECIMAL(15, 2), nullable=False, default=0.00, index=True)

    # GST Logic
    is_interstate = Column(Boolean, nullable=False, default=False)
    reverse_charge = Column(Boolean, nullable=False, default=False)

    # Bank Details
    bank_name = Column(String(150), nullable=True)
    account_number = Column(String(60), nullable=True)
    ifsc_code = Column(String(25), nullable=True)
    payment_terms = Column(Text, nullable=True)

    # Verification & Metadata
    verification_type = Column(Enum("AUTO", "MANUAL", name="verification_type"), nullable=False, default="AUTO")
    confidence_score = Column(DECIMAL(5, 4), nullable=False, default=0.0000)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Compound Unique Key: Deduplication anchor
    __table_args__ = (
        UniqueConstraint("vendor_gstin", "invoice_number", "invoice_date", name="uq_vendor_invoice"),
    )

    # Relationships
    document = relationship("Document", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    item_index = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=False)
    hsn_sac_code = Column(String(15), nullable=True, index=True)
    quantity = Column(DECIMAL(12, 3), nullable=False, default=1.000)
    unit_of_measure = Column(String(30), nullable=True, default="NOS")
    unit_price = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    taxable_value = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    tax_rate = Column(DECIMAL(5, 2), nullable=False, default=0.00)
    cgst_rate = Column(DECIMAL(5, 2), nullable=False, default=0.00)
    cgst_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    sgst_rate = Column(DECIMAL(5, 2), nullable=False, default=0.00)
    sgst_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    igst_rate = Column(DECIMAL(5, 2), nullable=False, default=0.00)
    igst_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    total_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
