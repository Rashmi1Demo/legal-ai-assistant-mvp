import json
import hashlib
from pathlib import Path
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from .services.pdf_report import (
    generate_case_report_pdf,
    generate_offline_document_pdf,
)
from .database import Base, engine, get_db
from .models import CaseAnalysis, Matter, CaseDocument
from .schemas import MatterCreate, MatterOut, MatterStatusUpdate
from .services.ai import analyze_matter
from .services.case_agent import CaseAnalystAgent
from .services.document_processor import (
    DocumentProcessingError,
    combine_documents,
    extract_text_from_bytes,
)
from .services.pdf_report import generate_case_report_pdf, generate_offline_document_pdf


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Case Analyst - Legal AI Assessment MVP",
    version="2.0.0",
    description=(
        "Assessment MVP: legal document upload, automatic text extraction, Case Analyst AI Agent, "
        "Claude-ready LLM integration, structured legal report, and optional RAG retrieval."
    ),
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

STATIC_DIR = Path(__file__).parent / "static"

case_agent = CaseAnalystAgent(
    top_k=2,
    retrieval_threshold=0.05
)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Case Analyst Legal AI Assessment MVP"
    }


@app.post("/cases/analyze")
async def analyze_case(
    files: List[UploadFile] = File(...),
    language: str = Form("en"),
    db: Session = Depends(get_db),
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="Upload at least one legal document."
        )

    # --------------------------------------------------
    # STEP 1: Extract text from uploaded documents
    # --------------------------------------------------

    extracted_documents: list[tuple[str, str]] = []

    for uploaded in files:
        filename = uploaded.filename or "uploaded_document"
        content = await uploaded.read()

        try:
            text = extract_text_from_bytes(
                filename,
                content
            )

        except DocumentProcessingError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc)
            ) from exc

        extracted_documents.append(
            (filename, text)
        )

    # --------------------------------------------------
    # STEP 2: Combine extracted document text
    # --------------------------------------------------

    combined_text = combine_documents(
        extracted_documents
    )

    # Generate hash from document content only.
    # Filename is intentionally excluded.
    content_for_hash = "\n\n".join(
        text.strip()
        for _, text in extracted_documents
    )

    document_hash = hashlib.sha256(
        content_for_hash.encode("utf-8")
    ).hexdigest()

    filenames = [
        name
        for name, _ in extracted_documents
    ]

    document_record = CaseDocument(
        filenames=json.dumps(filenames),
        extracted_text=combined_text,
        extracted_characters=len(combined_text),
        processing_status="Extracted"
    )

    db.add(document_record)
    db.commit()
    db.refresh(document_record)

    

    # --------------------------------------------------
    # STEP 3: Try AI analysis
    # --------------------------------------------------

    try:
        result = case_agent.analyze(
            combined_text,
            language=language
        )

    # --------------------------------------------------
    # STEP 4: NO AI / OFFLINE FALLBACK
    # --------------------------------------------------

    except Exception as exc:
        #print("AI ANALYSIS ERROR:", repr(exc))

        # Find previous AI analysis for the same documents
        previous_analysis = (
            db.query(CaseAnalysis)
            .filter(CaseAnalysis.document_hash == document_hash)
            .order_by(CaseAnalysis.id.desc())
            .first()
        )

        # Previous AI analysis found in PostgreSQL
        if previous_analysis:

            return {
                "analysis_id": previous_analysis.id,
                "document_id": document_record.id,
                "filenames": json.loads(previous_analysis.filenames),
                "extracted_characters": len(combined_text),

                "offline_mode": True,
                "ai_available": False,
                "stored_ai_analysis": True,

                "message": (
                    "AI is currently unavailable. "
                    "Displaying the latest previously generated "
                    "AI analysis retrieved from PostgreSQL."
                ),

                "extracted_content": None,

                "llm_provider": previous_analysis.llm_provider,
                "llm_model": previous_analysis.llm_model,

                "knowledge_sources": json.loads(
                    previous_analysis.knowledge_sources_json or "[]"
                ),

                "report": json.loads(
                    previous_analysis.report_json
                ),

                "created_at": previous_analysis.created_at,
            }

        # No previous AI analysis found
        return {
            "analysis_id": None,
            "document_id": document_record.id,
            "filenames": filenames,
            "extracted_characters": len(combined_text),

            "offline_mode": True,
            "ai_available": False,
            "stored_ai_analysis": False,

            "message": (
                "AI is currently unavailable and no previous "
                "AI analysis was found for these documents."
            ),

            "extracted_content": combined_text,

            "llm_provider": "Offline / No AI",
            "llm_model": "Not available",

            "knowledge_sources": [],
            "report": None,
        }

        filenames = [
            name
            for name, _ in extracted_documents
        ]

        return {
            "analysis_id": None,
            "document_id": document_record.id,

            "filenames": filenames,

            "extracted_characters": len(combined_text),

            "offline_mode": True,

            "ai_available": False,

            "message": (
                "AI analysis is currently unavailable. "
                "The legal documents were still processed successfully. "
                "The extracted document content is available below."
            ),

            "extracted_content": combined_text,

            "llm_provider": "Offline / No AI",

            "llm_model": "Not available",

            "knowledge_sources": [],

            "report": None,
        }

    # --------------------------------------------------
    # STEP 5: AI SUCCESS - SAVE RESULT
    # --------------------------------------------------

    filenames = [
        name
        for name, _ in extracted_documents
    ]

    record = CaseAnalysis(
    filenames=json.dumps(filenames),

    document_hash=document_hash,

    report_json=json.dumps(
        result["report"],
        ensure_ascii=False
    ),

    llm_provider=result["llm_provider"],

    llm_model=result["llm_model"],

    knowledge_sources_json=json.dumps(
        result["knowledge_sources"],
        ensure_ascii=False
    ),
)

    db.add(record)
    db.commit()
    db.refresh(record)

    # --------------------------------------------------
    # STEP 6: Return AI result
    # --------------------------------------------------

    return {
        "analysis_id": record.id,
        "filenames": filenames,
        "extracted_characters": len(combined_text),
        "offline_mode": False,
        "ai_available": True,
        **result,
        "created_at": record.created_at,
    }


@app.get("/cases/recent")
def recent_case_analyses(
    limit: int = 5,
    db: Session = Depends(get_db)
):
    limit = min(max(limit, 1), 20)

    records = (
        db.query(CaseAnalysis)
        .order_by(CaseAnalysis.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "analysis_id": item.id,
            "filenames": json.loads(item.filenames),
            "report": json.loads(item.report_json),
            "llm_provider": item.llm_provider,
            "llm_model": item.llm_model,
            "knowledge_sources": json.loads(
                item.knowledge_sources_json or "[]"
            ),
            "created_at": item.created_at,
        }
        for item in records
    ]


@app.get("/cases/{analysis_id}/pdf")
def download_case_pdf(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(CaseAnalysis)
        .filter(CaseAnalysis.id == analysis_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Case analysis not found",
        )

    case_data = {
        "provider": record.llm_provider,
        "model": record.llm_model,
        "report": json.loads(record.report_json),
    }

    pdf_buffer = generate_case_report_pdf(
        case_data
    )

    filename = (
        f"case_analysis_{analysis_id}.pdf"
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


# ------------------------------------------------------
# Existing matter-intake endpoints
# ------------------------------------------------------

@app.post("/matters", response_model=MatterOut)
def create_matter(
    payload: MatterCreate,
    db: Session = Depends(get_db)
):
    analysis = analyze_matter(
        payload.title,
        payload.description,
        payload.client_name
    )

    matter = Matter(
        title=payload.title,
        description=payload.description,
        client_name=payload.client_name,
        practice_area=analysis["practice_area"],
        priority=analysis["priority"],
        ai_summary=analysis["ai_summary"],
        suggested_next_step=analysis["suggested_next_step"],
        knowledge_source=analysis["knowledge_source"],
        status="New",
    )

    db.add(matter)
    db.commit()
    db.refresh(matter)

    return matter


@app.get("/matters", response_model=list[MatterOut])
def list_matters(
    db: Session = Depends(get_db)
):
    return (
        db.query(Matter)
        .order_by(Matter.id.desc())
        .all()
    )


@app.get(
    "/matters/{matter_id}",
    response_model=MatterOut
)
def get_matter(
    matter_id: int,
    db: Session = Depends(get_db)
):
    matter = (
        db.query(Matter)
        .filter(Matter.id == matter_id)
        .first()
    )

    if not matter:
        raise HTTPException(
            status_code=404,
            detail="Matter not found"
        )

    return matter


@app.patch(
    "/matters/{matter_id}/status",
    response_model=MatterOut
)
def update_matter_status(
    matter_id: int,
    payload: MatterStatusUpdate,
    db: Session = Depends(get_db)
):
    allowed = {
        "New",
        "Under Review",
        "Assigned",
        "Completed"
    }

    if payload.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=(
                "Status must be one of: "
                f"{', '.join(sorted(allowed))}"
            )
        )

    matter = (
        db.query(Matter)
        .filter(Matter.id == matter_id)
        .first()
    )

    if not matter:
        raise HTTPException(
            status_code=404,
            detail="Matter not found"
        )

    matter.status = payload.status

    db.commit()
    db.refresh(matter)

    return matter


@app.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db)
):
    total = (
        db.query(func.count(Matter.id))
        .scalar() or 0
    )

    new_count = (
        db.query(func.count(Matter.id))
        .filter(Matter.status == "New")
        .scalar() or 0
    )

    under_review = (
        db.query(func.count(Matter.id))
        .filter(Matter.status == "Under Review")
        .scalar() or 0
    )

    completed = (
        db.query(func.count(Matter.id))
        .filter(Matter.status == "Completed")
        .scalar() or 0
    )

    high = (
        db.query(func.count(Matter.id))
        .filter(Matter.priority == "High")
        .scalar() or 0
    )

    return {
        "total": total,
        "new": new_count,
        "under_review": under_review,
        "completed": completed,
        "high_priority": high,
    }

@app.get("/case-documents/{document_id}/pdf")
def download_offline_document_pdf(
    document_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(CaseDocument)
        .filter(CaseDocument.id == document_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    pdf_buffer = generate_offline_document_pdf(record)

    filename = f"offline_document_{document_id}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )    