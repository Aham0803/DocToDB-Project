import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# Base directory for backend
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "DocToDB GST Intelligent Pipeline"
    API_SECRET_KEY: str = "doctodb_secret_api_key_2026_secure"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # LLM Provider: 'gemini' | 'openai' | 'anthropic' | 'ollama'
    LLM_PROVIDER: str = "gemini"
    
    # Model configs
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.5-flash"
    
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2-vision"
    
    # MySQL Database Configuration
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "doc_to_db"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    
    @property
    def DATABASE_URL(self) -> str:
        # Safe URL generation for PyMySQL
        pwd = f":{self.MYSQL_PASSWORD}" if self.MYSQL_PASSWORD else ""
        return f"mysql+pymysql://{self.MYSQL_USER}{pwd}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"

    # ChromaDB Vector Store
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "financial_invoices"
    
    # Uploads Storage
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    
    # Validation & Autonomy Thresholds
    CONFIDENCE_AUTO_APPROVE_THRESHOLD: float = 0.88
    MAX_SELF_CORRECTION_RETRIES: int = 1
    
    # Langfuse Observability
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    class Config:
        env_file = (BASE_DIR.parent / ".env", BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Ensure critical local directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
