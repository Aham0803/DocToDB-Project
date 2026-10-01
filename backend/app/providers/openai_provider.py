import json
import base64
import logging
from typing import Tuple, List, Optional, Dict, Any
from app.providers.base import BaseLLMProvider
from app.providers.prompt_templates import (
    UNIVERSAL_EXTRACTION_SYSTEM_PROMPT,
    INVOICE_EXTRACTION_SYSTEM_PROMPT,
    REFINEMENT_PROMPT_TEMPLATE,
    RAG_CHAT_SYSTEM_PROMPT,
)
from app.schemas.invoice_schema import InvoiceSchema
from app.config import settings

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4o / GPT-4o-mini Multimodal Provider."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.OPENAI_MODEL
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key or self.api_key.startswith("your_"):
            return
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"OpenAI client initialized with model '{self.model_name}'")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self._client = None

    @property
    def provider_name(self) -> str:
        return "openai"

    async def extract_document(
        self,
        file_bytes: bytes,
        mime_type: str,
        filename: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Optional[float]]:
        if not self._client:
            raise ValueError("OpenAI client not initialized. Check OPENAI_API_KEY in .env")

        b64 = base64.b64encode(file_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64}"

        messages = [
            {"role": "system", "content": UNIVERSAL_EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all fields from this document into the universal JSON format."},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}}
                ]
            }
        ]

        response = await self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format={"type": "json_object"}
        )
        raw_text = response.choices[0].message.content
        data = json.loads(raw_text)
        conf = data.pop("_confidence", 0.92)
        return data, float(conf)

    async def extract_invoice(
        self,
        file_bytes: bytes,
        mime_type: str,
        filename: Optional[str] = None
    ) -> Tuple[InvoiceSchema, Optional[float]]:
        if not self._client:
            raise ValueError("OpenAI client not initialized. Check OPENAI_API_KEY in .env")

        b64 = base64.b64encode(file_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64}"

        messages = [
            {"role": "system", "content": INVOICE_EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all fields from this invoice into the specified JSON format."},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}}
                ]
            }
        ]

        response = await self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        conf = parsed.pop("_confidence", 0.90)
        return InvoiceSchema(**parsed), float(conf)

    async def refine_extraction(
        self,
        file_bytes: bytes,
        mime_type: str,
        previous_data: Dict[str, Any],
        validation_errors: List[str]
    ) -> Tuple[InvoiceSchema, Optional[float]]:
        if not self._client:
            return InvoiceSchema(**previous_data), 0.70

        b64 = base64.b64encode(file_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64}"

        error_bullets = "\n".join([f"- {err}" for err in validation_errors])
        prompt = REFINEMENT_PROMPT_TEMPLATE.format(
            error_list=error_bullets,
            previous_json=json.dumps(previous_data, indent=2)
        )

        messages = [
            {"role": "system", "content": "You are a meticulous financial auditor. Correct the errors specified."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]
            }
        ]

        response = await self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        parsed = json.loads(response.choices[0].message.content)
        conf = parsed.pop("_confidence", 0.92)
        return InvoiceSchema(**parsed), float(conf)

    async def generate_chat_answer(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        if not self._client:
            return f"Retrieved Context:\n{context}"

        messages = [
            {"role": "system", "content": RAG_CHAT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]

        res = await self._client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.2
        )
        return res.choices[0].message.content
