import os
from pathlib import Path

# Target directory
output_dir = Path(__file__).resolve().parent.parent.parent / "sample_invoices"
output_dir.mkdir(parents=True, exist_ok=True)

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_invoice_1():
    """Generates a 100% compliant Indian GST Tax Invoice (Intra-State Delhi -> Delhi)."""
    filename = str(output_dir / "Sample_GST_Invoice_01_Valid.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=1 # Center
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A')
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    mono_style = ParagraphStyle(
        'Mono',
        parent=body_style,
        fontName='Courier-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#0F766E')
    )

    # Header
    story.append(Paragraph("TAX INVOICE", title_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4F46E5'), spaceAfter=15))

    # Vendor & Invoice Details Table
    vendor_info = """
    <b>Apex Cloud Technologies Pvt Ltd</b><br/>
    Plot 42, Okhla Industrial Area Phase III<br/>
    New Delhi, 110020, India<br/>
    Phone: +91-11-45678901 | Email: accounts@apexcloud.in<br/>
    <b>GSTIN:</b> <font color="#4F46E5"><b>07AAAAA0000A1Z4</b></font><br/>
    <b>PAN:</b> AAAAA0000A
    """

    meta_info = """
    <b>Invoice No:</b> INV-2026-0891<br/>
    <b>Invoice Date:</b> 2026-03-15<br/>
    <b>Due Date:</b> 2026-04-15<br/>
    <b>Place of Supply:</b> 07-Delhi (Intra-State)<br/>
    <b>PO Number:</b> PO-99120
    """

    header_table = Table(
        [[Paragraph(vendor_info, body_style), Paragraph(meta_info, body_style)]],
        colWidths=[300, 240]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # Buyer Details
    buyer_info = """
    <b>Billed To (Customer):</b><br/>
    <b>Zenith Global Retail Ltd</b><br/>
    Tower B, Barakhamba Road, Connaught Place<br/>
    New Delhi, 110001, India<br/>
    <b>Customer GSTIN:</b> 07BBBBB1111B1ZP
    """
    story.append(Table([[Paragraph(buyer_info, body_style)]], colWidths=[540], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(Spacer(1, 15))

    # Items Table
    items_data = [
        ["#", "Item Description", "HSN/SAC", "Qty", "Unit Price", "Taxable", "CGST", "SGST", "Total (INR)"],
        ["1", "Dedicated Enterprise Server Hosting (March 2026)", "998313", "1", "30,000.00", "30,000.00", "2,700.00", "2,700.00", "35,400.00"],
        ["2", "Automated Daily Database Cloud Backups", "998315", "1", "20,000.00", "20,000.00", "1,800.00", "1,800.00", "23,600.00"],
    ]

    items_table = Table(items_data, colWidths=[20, 190, 55, 30, 60, 60, 40, 40, 65])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))

    # Totals Summary Table
    totals_data = [
        ["Taxable Subtotal:", "INR 50,000.00"],
        ["Central GST (CGST @ 9%):", "INR 4,500.00"],
        ["State GST (SGST @ 9%):", "INR 4,500.00"],
        ["Integrated GST (IGST):", "INR 0.00"],
        ["Total GST Tax Amount:", "INR 9,000.00"],
        ["Grand Total Payable:", "INR 59,000.00"]
    ]
    totals_table = Table(totals_data, colWidths=[380, 160])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 3),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 11),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#4F46E5')),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor('#4F46E5')),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 20))

    # Bank Details
    bank_text = """
    <b>Bank Account Details:</b><br/>
    Bank: <b>HDFC Bank Ltd</b> | Account No: <b>50200012345678</b> | IFSC: <b>HDFC0000123</b><br/>
    <b>Terms & Conditions:</b> Payment is due within 30 days of invoice date. All disputes subject to Delhi jurisdiction.
    """
    story.append(Table([[Paragraph(bank_text, body_style)]], colWidths=[540], style=[
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94A3B8')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))

    doc.build(story)
    print(f"Generated: {filename}")


def create_invoice_2_error():
    """Generates an Inter-State invoice with a math mismatch to demonstrate the HITL Review Screen."""
    filename = str(output_dir / "Sample_GST_Invoice_02_Review_Queue.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#991B1B'),
        alignment=1
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    story.append(Paragraph("TAX INVOICE", title_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#DC2626'), spaceAfter=15))

    vendor_info = """
    <b>Mumbai Precision Electronics Ltd</b><br/>
    Andheri East Industrial Hub, Mumbai, Maharashtra 400069<br/>
    <b>GSTIN:</b> <font color="#DC2626"><b>27AAAAA0000A1Z4</b></font><br/>
    <b>PAN:</b> AAAAA0000A
    """
    meta_info = """
    <b>Invoice No:</b> BOM/2026/4011<br/>
    <b>Invoice Date:</b> 2026-03-20<br/>
    <b>Place of Supply:</b> 07-Delhi (Inter-State)<br/>
    """
    story.append(Table([[Paragraph(vendor_info, body_style), Paragraph(meta_info, body_style)]], colWidths=[300, 240]))
    story.append(Spacer(1, 15))

    buyer_info = """
    <b>Customer Details:</b><br/>
    <b>Delhi Cyber Networks Ltd</b><br/>
    Nehru Place, New Delhi, 110019<br/>
    <b>GSTIN:</b> 07BBBBB1111B1ZP
    """
    story.append(Table([[Paragraph(buyer_info, body_style)]], colWidths=[540], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF2F2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#FCA5A5')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(Spacer(1, 15))

    items_data = [
        ["#", "Item Description", "HSN", "Qty", "Price", "Taxable", "IGST", "Total"],
        ["1", "Industrial Network Switches 48-Port", "851762", "2", "40,000.00", "80,000.00", "14,400.00", "94,400.00"],
        ["2", "Cat-6 High Speed Patch Cables (100m)", "854449", "5", "2,000.00", "10,000.00", "1,800.00", "11,800.00"],
    ]
    items_table = Table(items_data, colWidths=[20, 220, 50, 30, 60, 60, 40, 60])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#991B1B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))

    # Math Discrepancy (Subtotal 90,000 + Tax 16,200 = 106,200, but printed 115,000)
    totals_data = [
        ["Subtotal Taxable:", "INR 90,000.00"],
        ["Integrated GST (IGST @ 18%):", "INR 16,200.00"],
        ["Grand Total Payable (Math Mismatch):", "INR 115,000.00"]
    ]
    totals_table = Table(totals_data, colWidths=[380, 160])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 3),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#DC2626')),
    ]))
    story.append(totals_table)

    doc.build(story)
    print(f"Generated: {filename}")

if __name__ == "__main__":
    create_invoice_1()
    create_invoice_2_error()
