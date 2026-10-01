from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Enum, JSON, DateTime, text
from app.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_query = Column(Text, nullable=False)
    query_type = Column(
        Enum("STRUCTURED_SQL_TOOL", "VECTOR_RAG", "HYBRID", name="chat_query_type"),
        nullable=False
    )
    tool_called = Column(String(100), nullable=True)
    retrieved_sources = Column(JSON, nullable=True)
    assistant_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
