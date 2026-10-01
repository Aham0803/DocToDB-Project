import logging
from typing import Optional
from app.providers.base import BaseLLMProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider
from app.config import settings

logger = logging.getLogger(__name__)

# Singletons cache
_providers = {}

def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """
    Factory to retrieve or instantiate the chosen LLM provider.
    Defaults to settings.LLM_PROVIDER ('gemini').
    """
    name = (provider_name or settings.LLM_PROVIDER).lower()

    if name in _providers:
        return _providers[name]

    if name == "gemini":
        provider = GeminiProvider()
    elif name == "openai":
        provider = OpenAIProvider()
    else:
        logger.warning(f"Unknown or unconfigured provider '{name}'. Falling back to Gemini.")
        provider = GeminiProvider()

    _providers[name] = provider
    return provider
