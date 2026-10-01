import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_invoices"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_resume_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Sample_Resume_Senior_Engineer.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('RTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#1a365d'))
    sub_style = ParagraphStyle('RSub', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#4a5568'))
    sec_style = ParagraphStyle('RSec', parent=styles['Heading2'], fontSize=13, leading=17, textColor=colors.HexColor('#2b6cb0'), spaceBefore=10, spaceAfter=4)
    body_style = ParagraphStyle('RBody', parent=styles['Normal'], fontSize=9.5, leading=13, textColor=colors.HexColor('#2d3748'))

    story.append(Paragraph("RAHUL VERMA", title_style))
    story.append(Paragraph("Senior Full-Stack & AI Systems Architect | Bangalore, India", sub_style))
    story.append(Paragraph("Email: rahul.verma@example.com | Phone: +91-9876543210 | GitHub: github.com/rahulverma", sub_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("EXECUTIVE SUMMARY", sec_style))
    story.append(Paragraph("Versatile Lead Software Engineer with 7+ years of experience designing scalable microservices, LangChain/LangGraph pipelines, and enterprise PostgreSQL/MySQL databases. Proven track record leading distributed engineering teams.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("CORE SKILLS & TECHNOLOGIES", sec_style))
    skills_data = [
        ["Programming Languages:", "Python, TypeScript, Go, SQL"],
        ["Frameworks & AI:", "FastAPI, LangGraph, ChromaDB, PyTorch, React, Next.js"],
        ["Cloud & DevOps:", "Docker, Kubernetes, AWS (S3, ECS), CI/CD, Redis"],
        ["Databases:", "PostgreSQL, MySQL, SQLite, MongoDB"]
    ]
    t = Table(skills_data, colWidths=[150, 380])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#2b6cb0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("WORK EXPERIENCE", sec_style))
    story.append(Paragraph("<b>Lead AI Engineer</b> — Nexus Cloud Systems (2022 - Present)", body_style))
    story.append(Paragraph("• Architected multi-tenant RAG pipeline handling 100k daily queries with sub-second latency.<br/>• Reduced document processing errors by 40% via automated self-correcting validation agents.", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Senior Backend Developer</b> — FinTech Solutions Ltd (2019 - 2022)", body_style))
    story.append(Paragraph("• Implemented automated GST invoice reconciliation engine processing ₹50Cr monthly transactions.<br/>• Optimized relational database queries reducing P99 latency from 1.2s to 85ms.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("EDUCATION & CERTIFICATIONS", sec_style))
    story.append(Paragraph("<b>B.Tech in Computer Science & Engineering</b> — National Institute of Technology (2015 - 2019)<br/>AWS Certified Solutions Architect - Associate", body_style))

    doc.build(story)
    print(f"Created: {pdf_path}")

def create_medical_report_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Sample_Medical_Lab_Report.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('MTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#134e4a'), alignment=1)
    sub_style = ParagraphStyle('MSub', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#4b5563'), alignment=1)
    sec_style = ParagraphStyle('MSec', parent=styles['Heading2'], fontSize=12, leading=15, textColor=colors.HexColor('#0d9488'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('MBody', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#1f2937'))

    story.append(Paragraph("APEX DIAGNOSTIC LABORATORIES & HEALTHCARE", title_style))
    story.append(Paragraph("NABL Accredited Medical Testing Center | Ring Road, New Delhi 110029 | Tel: 011-26543210", sub_style))
    story.append(Spacer(1, 10))

    patient_data = [
        ["Patient Name:", "Mrs. Priya Sharma", "Age / Gender:", "34 Yrs / Female"],
        ["Patient ID / UHID:", "APX-2026-9812", "Referred By:", "Dr. Arvind Mehta, MD"],
        ["Sample Collection:", "2026-03-20 08:30 AM", "Report Date:", "2026-03-20 02:15 PM"],
        ["Test Name:", "Comprehensive Metabolic & Lipid Panel", "Sample Type:", "Blood Serum"]
    ]
    pt_table = Table(patient_data, colWidths=[110, 160, 110, 150])
    pt_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdfa')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#99f6e4')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ccfbf1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(pt_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("INVESTIGATION FINDINGS", sec_style))
    test_results = [
        ["Test Parameter", "Observed Value", "Standard Unit", "Biological Reference Range", "Status"],
        ["Fasting Blood Sugar", "94.0", "mg/dL", "70.0 - 100.0", "NORMAL"],
        ["Serum Cholesterol - Total", "218.0", "mg/dL", "< 200.0", "BORDERLINE HIGH"],
        ["HDL Cholesterol (Good)", "52.0", "mg/dL", "> 50.0", "OPTIMAL"],
        ["LDL Cholesterol (Calculated)", "138.0", "mg/dL", "< 100.0", "MILD ELEVATION"],
        ["Serum Triglycerides", "140.0", "mg/dL", "< 150.0", "NORMAL"],
        ["Serum Creatinine", "0.85", "mg/dL", "0.60 - 1.10", "NORMAL"],
        ["Hemoglobin (Hb)", "13.2", "g/dL", "12.0 - 15.5", "NORMAL"]
    ]
    res_table = Table(test_results, colWidths=[150, 85, 75, 140, 80])
    res_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(res_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("CLINICAL DIAGNOSIS & PHYSICIAN RECOMMENDATIONS", sec_style))
    story.append(Paragraph("<b>Primary Clinical Impression:</b> Mild Hyperlipidemia with optimal renal and glycemic parameters.<br/>"
                           "<b>Prescribed Plan & Medications:</b><br/>"
                           "1. Tab Atorvastatin 10mg once daily at bedtime for 60 days.<br/>"
                           "2. Dietary modification: Reduce saturated fats and increase soluble fiber.<br/>"
                           "3. Follow-up lipid profile retest recommended after 8 weeks.", body_style))

    doc.build(story)
    print(f"Created: {pdf_path}")

def create_legal_contract_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Sample_Legal_Service_Agreement.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('LTitle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#431407'), alignment=1)
    sub_style = ParagraphStyle('LSub', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#78350f'), alignment=1)
    sec_style = ParagraphStyle('LSec', parent=styles['Heading2'], fontSize=11, leading=14, textColor=colors.HexColor('#9a3412'), spaceBefore=8, spaceAfter=3)
    body_style = ParagraphStyle('LBody', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=colors.HexColor('#1c1917'))

    story.append(Paragraph("MASTER SERVICES AGREEMENT", title_style))
    story.append(Paragraph("Contract Reference: MSA-2026-HZN-099 | Effective Date: 2026-04-01", sub_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("PARTIES TO THE AGREEMENT", sec_style))
    story.append(Paragraph("This Master Services Agreement ('Agreement') is entered into as of April 1, 2026 by and between:<br/>"
                           "<b>SERVICE PROVIDER:</b> Horizon Innovations Pvt Ltd, having its corporate office at Tech Park, Outer Ring Road, Bangalore 560103.<br/>"
                           "<b>CLIENT:</b> Nova Global Enterprises Corp, having its principal place of business at 500 Madison Avenue, New York, NY 10022.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. SCOPE OF SERVICES & DELIVERABLES", sec_style))
    story.append(Paragraph("Service Provider shall deliver cloud infrastructure migration, DevOps automated CI/CD pipelines, and 24/7 security operations monitoring as outlined in Statement of Work (SOW-01). All deliverables must satisfy agreed service level metrics.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. COMMERCIAL TERMS & FEES", sec_style))
    story.append(Paragraph("Total Contract Value: <b>USD $120,000.00</b> (Payable in monthly installments of $10,000.00 upon milestone sign-off). Payment terms: Net 30 days from invoice generation. Late payments shall incur interest at 1.5% per month.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. CONFIDENTIALITY & INTELLECTUAL PROPERTY", sec_style))
    story.append(Paragraph("Both parties agree to protect Proprietary Information with at least the standard of care used for their own sensitive trade secrets. Client shall retain sole ownership of all pre-existing IP and custom work products generated under this Agreement.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. TERM & TERMINATION CLAUSE", sec_style))
    story.append(Paragraph("The initial term shall be twelve (12) months. Either party may terminate this Agreement without cause upon sixty (60) days written notice, or immediately for material breach uncured within thirty (30) days.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("5. GOVERNING LAW & JURISDICTION", sec_style))
    story.append(Paragraph("This Agreement shall be governed by and construed in accordance with the laws of Delaware, USA. Any unresolved dispute shall be settled by binding arbitration in New York.", body_style))

    doc.build(story)
    print(f"Created: {pdf_path}")

if __name__ == "__main__":
    create_resume_pdf()
    create_medical_report_pdf()
    create_legal_contract_pdf()
    print("All sample universal documents generated successfully!")
