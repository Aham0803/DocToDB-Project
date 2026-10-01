import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import func
from app.database import SessionLocal
from app.models.invoice import Invoice, InvoiceItem
from app.services.rag_service import rag_service
from app.providers.factory import get_llm_provider
from app.schemas.chat_schema import ChatResponse, SourceCitation

logger = logging.getLogger(__name__)

class QueryRouter:
    """
    Hybrid Query Router:
    Distinguishes between structured aggregation/filter queries and unstructured semantic queries.
    Uses SAFE, FIXED MySQL tools (no free-form text-to-SQL) for numbers, and ChromaDB for text/policy RAG.
    """

    def __init__(self):
        pass

    def classify_intent(self, query: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Classifies user query into:
        - ('STRUCTURED_SQL_TOOL', tool_name, params)
        - ('VECTOR_RAG', 'chroma_search', {'query': query})
        """
        q = query.lower().strip()

        # 1. Invoice Number lookup
        inv_match = re.search(r"\b(inv[-_\w\d]+|\d{4,8})\b", q)
        if any(w in q for w in ["invoice", "bill", "number", "details"]) and inv_match:
            return "STRUCTURED_SQL_TOOL", "get_invoice_by_number", {"invoice_number": inv_match.group(1)}

        # 2. Unpaid / Pending / Overdue
        if any(w in q for w in ["pending", "unpaid", "baki", "due", "overdue", "balance"]):
            vendor = self._extract_vendor_hint(q)
            return "STRUCTURED_SQL_TOOL", "get_unpaid_invoices", {"vendor_name": vendor}

        # 3. Sum / Total / Count Aggregation
        if any(w in q for w in ["sum", "total amount", "kul rashi", "kitna hua", "turnover", "total spend"]):
            vendor = self._extract_vendor_hint(q)
            return "STRUCTURED_SQL_TOOL", "sum_by_vendor", {"vendor_name": vendor}

        # 4. Tax Breakdown
        if any(w in q for w in ["cgst", "sgst", "igst", "tax summary", "tax total", "kitna tax"]):
            vendor = self._extract_vendor_hint(q)
            return "STRUCTURED_SQL_TOOL", "get_tax_breakdown", {"vendor_name": vendor}

        # 5. List / Filter Invoices by Vendor
        if any(w in q for w in ["saare invoice", "all invoices", "list", "show invoices", "kitne invoice"]):
            vendor = self._extract_vendor_hint(q)
            return "STRUCTURED_SQL_TOOL", "get_invoices_by_vendor", {"vendor_name": vendor}

        # Default: Fallback to ChromaDB Semantic RAG
        return "VECTOR_RAG", "chroma_vector_rag", {"query": query}

    def _extract_vendor_hint(self, query: str) -> Optional[str]:
        """Extracts potential vendor name keywords from query."""
        stop_words = {
            "vendor", "ke", "ka", "ki", "saare", "all", "invoices", "invoice", "bills", "pending",
            "balance", "total", "amount", "wala", "wale", "wali", "dikhao", "batao", "show", "me",
            "what", "is", "the", "for", "from", "sum", "and", "or", "in", "kitna", "hai"
        }
        words = re.findall(r"\b[A-Za-z0-9]+\b", query)
        candidates = [w for w in words if w.lower() not in stop_words and len(w) > 2]
        return candidates[0] if candidates else None

    # ========================================================
    # Predefined Deterministic MySQL Tools (Safe Parameterized)
    # ========================================================

    def tool_get_invoice_by_number(self, invoice_number: str) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            inv = db.query(Invoice).filter(Invoice.invoice_number.ilike(f"%{invoice_number}%")).first()
            if not inv:
                return {"found": False, "message": f"No invoice found matching '{invoice_number}'."}

            items = [
                {
                    "item": it.description,
                    "qty": float(it.quantity),
                    "price": float(it.unit_price),
                    "tax_rate": float(it.tax_rate),
                    "total": float(it.total_amount)
                } for it in inv.items
            ]

            return {
                "found": True,
                "invoice_number": inv.invoice_number,
                "vendor_name": inv.vendor_name,
                "vendor_gstin": inv.vendor_gstin,
                "invoice_date": str(inv.invoice_date),
                "due_date": str(inv.due_date) if inv.due_date else "N/A",
                "payment_status": inv.payment_status,
                "subtotal": float(inv.subtotal_amount),
                "total_tax": float(inv.total_tax_amount),
                "grand_total": float(inv.grand_total),
                "items": items
            }
        finally:
            db.close()

    def tool_get_unpaid_invoices(self, vendor_name: Optional[str] = None) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            q = db.query(Invoice).filter(Invoice.payment_status.in_(["PENDING", "OVERDUE", "PARTIALLY_PAID"]))
            if vendor_name:
                q = q.filter(Invoice.vendor_name.ilike(f"%{vendor_name}%"))

            records = q.all()
            total_unpaid = sum(float(r.grand_total) for r in records)
            return {
                "count": len(records),
                "total_unpaid_amount": total_unpaid,
                "invoices": [
                    {
                        "invoice_number": r.invoice_number,
                        "vendor_name": r.vendor_name,
                        "invoice_date": str(r.invoice_date),
                        "due_date": str(r.due_date) if r.due_date else "N/A",
                        "status": r.payment_status,
                        "amount": float(r.grand_total)
                    } for r in records
                ]
            }
        finally:
            db.close()

    def tool_sum_by_vendor(self, vendor_name: Optional[str] = None) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            q = db.query(
                func.count(Invoice.id).label("count"),
                func.sum(Invoice.subtotal_amount).label("subtotal"),
                func.sum(Invoice.total_tax_amount).label("total_tax"),
                func.sum(Invoice.grand_total).label("grand_total")
            )
            if vendor_name:
                q = q.filter(Invoice.vendor_name.ilike(f"%{vendor_name}%"))

            res = q.first()
            return {
                "vendor_filter": vendor_name or "ALL_VENDORS",
                "invoice_count": res.count or 0,
                "total_subtotal": float(res.subtotal or 0.0),
                "total_tax": float(res.total_tax or 0.0),
                "total_grand_total": float(res.grand_total or 0.0)
            }
        finally:
            db.close()

    def tool_get_tax_breakdown(self, vendor_name: Optional[str] = None) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            q = db.query(
                func.sum(Invoice.cgst_amount).label("cgst"),
                func.sum(Invoice.sgst_amount).label("sgst"),
                func.sum(Invoice.igst_amount).label("igst"),
                func.sum(Invoice.total_tax_amount).label("total_tax")
            )
            if vendor_name:
                q = q.filter(Invoice.vendor_name.ilike(f"%{vendor_name}%"))

            res = q.first()
            return {
                "vendor_filter": vendor_name or "ALL_VENDORS",
                "total_cgst": float(res.cgst or 0.0),
                "total_sgst": float(res.sgst or 0.0),
                "total_igst": float(res.igst or 0.0),
                "total_tax": float(res.total_tax or 0.0)
            }
        finally:
            db.close()

    def tool_get_invoices_by_vendor(self, vendor_name: Optional[str] = None) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            q = db.query(Invoice)
            if vendor_name:
                q = q.filter(Invoice.vendor_name.ilike(f"%{vendor_name}%"))

            records = q.order_by(Invoice.invoice_date.desc()).limit(20).all()
            return {
                "count": len(records),
                "invoices": [
                    {
                        "invoice_number": r.invoice_number,
                        "vendor_name": r.vendor_name,
                        "date": str(r.invoice_date),
                        "status": r.payment_status,
                        "grand_total": float(r.grand_total)
                    } for r in records
                ]
            }
        finally:
            db.close()

    # ========================================================
    # Main Execution Flow
    # ========================================================

    async def execute_query(self, user_query: str) -> ChatResponse:
        intent_type, tool_name, params = self.classify_intent(user_query)
        provider = get_llm_provider()
        citations: List[SourceCitation] = []

        if intent_type == "STRUCTURED_SQL_TOOL":
            # Execute deterministic safe MySQL tool
            tool_fn = getattr(self, f"tool_{tool_name}", None)
            if tool_fn:
                result_data = tool_fn(**params)
            else:
                result_data = {"error": "Tool not recognized"}

            # Synthesize human friendly answer with LLM using tool data
            context_str = f"Tool '{tool_name}' returned deterministic database data:\n{result_data}"
            answer = await provider.generate_chat_answer(user_query, context_str)

            # Build citations
            if "invoices" in result_data:
                for inv in result_data["invoices"][:3]:
                    citations.append(SourceCitation(
                        source_type="database_record",
                        invoice_number=inv.get("invoice_number"),
                        vendor_name=inv.get("vendor_name"),
                        snippet=f"Status: {inv.get('status')}, Amount: ₹{inv.get('amount', inv.get('grand_total', 0)):,.2f}"
                    ))
            elif "invoice_number" in result_data:
                citations.append(SourceCitation(
                    source_type="database_record",
                    invoice_number=result_data.get("invoice_number"),
                    vendor_name=result_data.get("vendor_name"),
                    snippet=f"Date: {result_data.get('invoice_date')}, Grand Total: ₹{result_data.get('grand_total', 0):,.2f}"
                ))

            return ChatResponse(
                query=user_query,
                query_type="STRUCTURED_SQL_TOOL",
                tool_called=tool_name,
                answer=answer,
                citations=citations,
                raw_data=result_data
            )

        else:
            # Semantic / Policy / Text Question -> ChromaDB RAG
            chunks = rag_service.search(user_query, n_results=4)
            if chunks:
                context_str = "\n\n".join([f"--- CHUNK ---\n{c['text']}" for c in chunks])
                for c in chunks:
                    meta = c.get("metadata", {})
                    citations.append(SourceCitation(
                        source_type="vector_document",
                        invoice_number=meta.get("invoice_no"),
                        vendor_name=meta.get("vendor"),
                        snippet=c["text"][:140] + "...",
                        document_id=meta.get("doc_id"),
                        score=round(1.0 - float(c.get("distance", 0.0)), 3)
                    ))
            else:
                context_str = "No specific semantic chunks found in ChromaDB."

            answer = await provider.generate_chat_answer(user_query, context_str)

            return ChatResponse(
                query=user_query,
                query_type="VECTOR_RAG",
                tool_called="chroma_vector_rag",
                answer=answer,
                citations=citations,
                raw_data=None
            )

query_router = QueryRouter()
