import os
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    """Manages document chunking, embeddings, and vector similarity search via ChromaDB."""

    def __init__(self):
        self._client = None
        self._collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
            self._client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            self._collection = self._client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB initialized at '{settings.CHROMA_PERSIST_DIR}' (Collection: '{settings.CHROMA_COLLECTION_NAME}')")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self._client = None
            self._collection = None

    def index_invoice(self, doc_id: str, data: Dict[str, Any]):
        """Creates semantic chunks for an invoice and stores in ChromaDB."""
        if not self._collection:
            logger.warning("ChromaDB collection unavailable; skipping vector indexing.")
            return

        doc_type = str(data.get("document_type", "GENERAL_DOCUMENT")).upper()
        chunks: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        # If document is a standard GST Invoice / Receipt
        inv_data = data.get("invoice_data") if isinstance(data.get("invoice_data"), dict) else data
        inv_no = inv_data.get("invoice_number") or data.get("identifier_number", "DOC")
        vendor = inv_data.get("vendor_name") or data.get("primary_entity", "Unknown")

        if inv_data.get("invoice_number") and inv_data.get("vendor_gstin"):
            v_gstin = inv_data.get("vendor_gstin", "UNKNOWN")
            customer = inv_data.get("customer_name", "UNKNOWN")
            inv_date = inv_data.get("invoice_date", "")
            grand_total = inv_data.get("grand_total", 0.0)

            # 1. Invoice Header & Parties Chunk
            header_text = (
                f"Tax Invoice: {inv_no}\n"
                f"Date: {inv_date}\n"
                f"Vendor / Supplier: {vendor} (GSTIN: {v_gstin}, PAN: {inv_data.get('vendor_pan', '')})\n"
                f"Vendor Address: {inv_data.get('vendor_address', '')}\n"
                f"Customer / Buyer: {customer} (GSTIN: {inv_data.get('customer_gstin', 'N/A')})\n"
                f"Place of Supply: {inv_data.get('place_of_supply', '')}\n"
                f"Grand Total: INR {grand_total:,.2f}"
            )
            chunks.append(header_text)
            metadatas.append({"doc_id": doc_id, "invoice_no": inv_no, "vendor": vendor, "doc_type": "INVOICE", "type": "header"})
            ids.append(f"{doc_id}_header")

            # 2. Line Items Details Chunk
            items = inv_data.get("items", [])
            if items:
                items_lines = [f"Invoice {inv_no} Line Items Breakdown:"]
                for idx, it in enumerate(items):
                    items_lines.append(
                        f"Item {idx+1}: {it.get('description', '')} | HSN: {it.get('hsn_sac_code', 'N/A')} | "
                        f"Qty: {it.get('quantity', 1)} {it.get('unit_of_measure', '')} | Unit Price: ₹{it.get('unit_price', 0):,.2f} | "
                        f"GST Rate: {it.get('tax_rate', 0)}% | Total Amount: ₹{it.get('total_amount', 0):,.2f}"
                    )
                chunks.append("\n".join(items_lines))
                metadatas.append({"doc_id": doc_id, "invoice_no": inv_no, "vendor": vendor, "doc_type": "INVOICE", "type": "items"})
                ids.append(f"{doc_id}_items")

            # 3. Tax Breakdown & Math Chunk
            tax_text = (
                f"Invoice {inv_no} Financials & Taxes:\n"
                f"Subtotal: ₹{inv_data.get('subtotal_amount', 0):,.2f}\n"
                f"CGST: ₹{inv_data.get('cgst_amount', 0):,.2f}\n"
                f"SGST: ₹{inv_data.get('sgst_amount', 0):,.2f}\n"
                f"IGST: ₹{inv_data.get('igst_amount', 0):,.2f}\n"
                f"Total Tax: ₹{inv_data.get('total_tax_amount', 0):,.2f}\n"
                f"Discount: ₹{inv_data.get('discount_amount', 0):,.2f}\n"
                f"Shipping: ₹{inv_data.get('shipping_amount', 0):,.2f}\n"
                f"Grand Total Payable: ₹{grand_total:,.2f}"
            )
            chunks.append(tax_text)
            metadatas.append({"doc_id": doc_id, "invoice_no": inv_no, "vendor": vendor, "doc_type": "INVOICE", "type": "financials"})
            ids.append(f"{doc_id}_financials")

            # 4. Bank Account & Terms Chunk
            if inv_data.get("bank_name") or inv_data.get("account_number") or inv_data.get("payment_terms"):
                bank_text = (
                    f"Invoice {inv_no} Payment & Bank Details:\n"
                    f"Bank: {inv_data.get('bank_name', 'N/A')}\n"
                    f"Account Number: {inv_data.get('account_number', 'N/A')}\n"
                    f"IFSC Code: {inv_data.get('ifsc_code', 'N/A')}\n"
                    f"Payment Terms: {inv_data.get('payment_terms', 'Standard')}"
                )
                chunks.append(bank_text)
                metadatas.append({"doc_id": doc_id, "invoice_no": inv_no, "vendor": vendor, "doc_type": "INVOICE", "type": "bank_terms"})
                ids.append(f"{doc_id}_bank_terms")

        # Universal Document Chunks (for all document types)
        title = data.get("document_title") or data.get("title", "Document")
        summary = data.get("summary", "")
        p_entity = data.get("primary_entity", "N/A")
        s_entity = data.get("secondary_entity", "N/A")
        d_date = data.get("document_date", "")

        summary_chunk = (
            f"Document Type: {doc_type}\n"
            f"Title: {title}\n"
            f"Date: {d_date}\n"
            f"Primary Subject / Entity: {p_entity}\n"
            f"Secondary Counterparty: {s_entity}\n"
            f"Reference / ID Number: {inv_no}\n"
            f"Executive Summary: {summary}"
        )
        chunks.append(summary_chunk)
        metadatas.append({"doc_id": doc_id, "doc_type": doc_type, "title": title, "entity": p_entity, "type": "summary"})
        ids.append(f"{doc_id}_summary")

        # Dynamic Key Fields Chunk
        key_fields = data.get("key_fields", {})
        if key_fields and isinstance(key_fields, dict):
            field_lines = [f"{title} Attributes & Fields:"]
            for k, v in key_fields.items():
                field_lines.append(f"- {k}: {v}")
            chunks.append("\n".join(field_lines))
            metadatas.append({"doc_id": doc_id, "doc_type": doc_type, "title": title, "type": "attributes"})
            ids.append(f"{doc_id}_attributes")

        # Tables Chunk
        tables = data.get("tables", [])
        if tables and isinstance(tables, list):
            for t_idx, tbl in enumerate(tables):
                t_name = tbl.get("table_name", f"Table {t_idx+1}")
                t_rows = tbl.get("rows", [])
                tbl_lines = [f"{title} - {t_name}:"]
                for r in t_rows[:20]:  # limit to top 20 rows per chunk
                    if isinstance(r, dict):
                        row_str = " | ".join([f"{rk}: {rv}" for rk, rv in r.items()])
                        tbl_lines.append(row_str)
                chunks.append("\n".join(tbl_lines))
                metadatas.append({"doc_id": doc_id, "doc_type": doc_type, "table": t_name, "type": "table"})
                ids.append(f"{doc_id}_table_{t_idx}")

        try:
            self._collection.upsert(
                ids=ids,
                documents=chunks,
                metadatas=metadatas
            )
            logger.info(f"Indexed {len(chunks)} chunks for {doc_type} '{title}' in ChromaDB")
        except Exception as e:
            logger.error(f"Error upserting to ChromaDB: {e}")


    def search(self, query: str, n_results: int = 4) -> List[Dict[str, Any]]:
        """Queries ChromaDB for semantic similarity chunks."""
        if not self._collection:
            return []

        try:
            res = self._collection.query(
                query_texts=[query],
                n_results=n_results
            )
            output = []
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            distances = res.get("distances", [[]])[0] if "distances" in res else [0.0] * len(docs)

            for doc_text, meta, dist in zip(docs, metas, distances):
                output.append({
                    "text": doc_text,
                    "metadata": meta,
                    "distance": dist
                })
            return output
        except Exception as e:
            logger.error(f"ChromaDB search query failed: {e}")
            return []

rag_service = RAGService()
