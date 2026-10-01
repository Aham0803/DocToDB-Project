from abc import ABC, abstractmethod
from typing import Tuple, List, Optional, Dict, Any
from app.schemas.invoice_schema import InvoiceSchema

class BaseLLMProvider(ABC):
    """Abstract interface for all multimodal invoice extraction & RAG chat providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of provider (e.g. 'gemini', 'openai', 'anthropic', 'ollama')."""
        pass

    @abstractmethod
    async def extract_document(
        self,
        file_bytes: bytes,
        mime_type: str,
        filename: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Optional[float]]:
        """
        Extract structured data from ANY document (Invoice, Resume, Medical, Contract, etc.).
        Returns (document_dict, raw_model_confidence).
        """
        pass

    @abstractmethod
    async def extract_invoice(
        self,
        file_bytes: bytes,
        mime_type: str,
        filename: Optional[str] = None
    ) -> Tuple[InvoiceSchema, Optional[float]]:
        """
        Extract structured GST invoice data from PDF or image bytes.
        Returns (InvoiceSchema, raw_model_confidence).
        """
        pass

    @abstractmethod
    async def refine_extraction(
        self,
        file_bytes: bytes,
        mime_type: str,
        previous_data: Dict[str, Any],
        validation_errors: List[str]
    ) -> Tuple[InvoiceSchema, Optional[float]]:
        """
        Self-Correction Retry Loop:
        Re-extract/correct specific fields when validation errors are detected.
        """
        pass

    @abstractmethod
    async def generate_chat_answer(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Synthesize an answer for the user query using retrieved RAG context / tool data.
        """
        pass
