from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy import Column, Integer, String, Text, DateTime


from .database import Base


class Matter(Base):
    __tablename__ = "matters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    description = Column(Text, nullable=False)
    client_name = Column(String(150), nullable=True)
    practice_area = Column(String(100), nullable=True)
    priority = Column(String(50), nullable=True)
    ai_summary = Column(Text, nullable=True)
    suggested_next_step = Column(Text, nullable=True)
    knowledge_source = Column(String(255), nullable=True)
    status = Column(String(50), default="New")
    created_at = Column(DateTime, default=datetime.utcnow)


class CaseAnalysis(Base):
    __tablename__ = "case_analyses"

    id = Column(Integer, primary_key=True, index=True)
    filenames = Column(Text, nullable=False)
    report_json = Column(Text, nullable=False)
    llm_provider = Column(String(120), nullable=True)
    llm_model = Column(String(120), nullable=True)
    knowledge_sources_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    document_hash = Column(String(64), index=True, nullable=True)


class CaseDocument(Base):
    __tablename__ = "case_documents"

    id = Column(Integer, primary_key=True, index=True)

    filenames = Column(Text, nullable=False)

    extracted_text = Column(Text, nullable=False)

    extracted_characters = Column(Integer, nullable=False)

    processing_status = Column(
        String(50),
        default="Extracted"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )    

    
