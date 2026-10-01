import json
from pathlib import Path
from typing import List, Dict, Any

# A representative sample of ground-truth labeled Indian GST invoices
BENCHMARK_DATASET: List[Dict[str, Any]] = [
    {
        "id": "GT-INV-001",
        "description": "Standard Intra-State IT Services (Delhi to Delhi) - 18% GST",
        "ground_truth": {
            "invoice_number": "DEL/2026/0142",
            "invoice_date": "2026-02-10",
            "vendor_name": "TechVentures Software India Pvt Ltd",
            "vendor_gstin": "07AAAAA0000A1Z4",
            "customer_name": "Metro Retailers Private Limited",
            "customer_gstin": "07BBBBB1111B1ZP",
            "place_of_supply": "07-Delhi",
            "subtotal_amount": 100000.00,
            "cgst_amount": 9000.00,
            "sgst_amount": 9000.00,
            "igst_amount": 0.00,
            "total_tax_amount": 18000.00,
            "grand_total": 118000.00,
            "is_interstate": False,
            "items_count": 2
        }
    },
    {
        "id": "GT-INV-002",
        "description": "Inter-State Electronics Hardware (Maharashtra to Karnataka) - 18% IGST",
        "ground_truth": {
            "invoice_number": "MH-BOM-8891",
            "invoice_date": "2026-02-14",
            "vendor_name": "Silicon Waves Semiconductors Ltd",
            "vendor_gstin": "27AAAAA0000A1Z4",
            "customer_name": "Bengaluru Cloud Dynamics LLP",
            "customer_gstin": "29CCCCC2222C1Z4",
            "place_of_supply": "29-Karnataka",
            "subtotal_amount": 250000.00,
            "cgst_amount": 0.00,
            "sgst_amount": 0.00,
            "igst_amount": 45000.00,
            "total_tax_amount": 45000.00,
            "grand_total": 295000.00,
            "is_interstate": True,
            "items_count": 3
        }
    },
    {
        "id": "GT-INV-003",
        "description": "Intra-State Manufacturing with 12% GST and Round Off (Gujarat to Gujarat)",
        "ground_truth": {
            "invoice_number": "GUJ-MFG-302",
            "invoice_date": "2026-02-18",
            "vendor_name": "Gujarat Precision Forgings Pvt Ltd",
            "vendor_gstin": "24AAAAA0000A1Z5",
            "customer_name": "Baroda Auto Ancillaries",
            "customer_gstin": "24DDDDD3333D1Z2",
            "place_of_supply": "24-Gujarat",
            "subtotal_amount": 83450.00,
            "cgst_amount": 5007.00,
            "sgst_amount": 5007.00,
            "igst_amount": 0.00,
            "total_tax_amount": 10014.00,
            "round_off_amount": -0.00,
            "grand_total": 93464.00,
            "is_interstate": False,
            "items_count": 4
        }
    },
    {
        "id": "GT-INV-004",
        "description": "Inter-State Freight & Logistics with 5% IGST (Haryana to UP)",
        "ground_truth": {
            "invoice_number": "LOG/26/9011",
            "invoice_date": "2026-02-22",
            "vendor_name": "North Express Movers & Cargo Ltd",
            "vendor_gstin": "06AAAAA0000A1Z5",
            "customer_name": "Noida Warehousing Hub",
            "customer_gstin": "09EEEEE4444E1Z1",
            "place_of_supply": "09-Uttar Pradesh",
            "subtotal_amount": 40000.00,
            "cgst_amount": 0.00,
            "sgst_amount": 0.00,
            "igst_amount": 2000.00,
            "total_tax_amount": 2000.00,
            "grand_total": 42000.00,
            "is_interstate": True,
            "items_count": 1
        }
    },
    {
        "id": "GT-INV-005",
        "description": "High Value Industrial Machinery with 28% GST (Tamil Nadu to Telangana)",
        "ground_truth": {
            "invoice_number": "CHE-IND-5010",
            "invoice_date": "2026-02-25",
            "vendor_name": "Madras Hydraulic Pumps Ltd",
            "vendor_gstin": "33AAAAA0000A1Z5",
            "customer_name": "Hyderabad Industrial Works",
            "customer_gstin": "36FFFFF5555F1Z0",
            "place_of_supply": "36-Telangana",
            "subtotal_amount": 500000.00,
            "cgst_amount": 0.00,
            "sgst_amount": 0.00,
            "igst_amount": 140000.00,
            "total_tax_amount": 140000.00,
            "grand_total": 640000.00,
            "is_interstate": True,
            "items_count": 2
        }
    }
]

def load_ground_truth_dataset() -> List[Dict[str, Any]]:
    return BENCHMARK_DATASET
