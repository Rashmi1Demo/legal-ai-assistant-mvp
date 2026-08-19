from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import Base, engine, get_db
from .models import Matter
from .schemas import MatterCreate, MatterOut, MatterStatusUpdate
from .services.ai import analyze_matter

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AlGhazzawi Legal AI Assistant - Demo MVP",
    version="1.0.0",
    description="Demo law firm AI MVP with FastAPI, matter intake, RAG retrieval, and local Ollama LLM."
)

STATIC_DIR = Path(__file__).parent / "static"

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "Legal AI Assistant Demo"}

@app.post("/matters", response_model=MatterOut)
def create_matter(payload: MatterCreate, db: Session = Depends(get_db)):
    analysis = analyze_matter(payload.title, payload.description, payload.client_name)

    matter = Matter(
        title=payload.title,
        description=payload.description,
        client_name=payload.client_name,
        practice_area=analysis["practice_area"],
        priority=analysis["priority"],
        ai_summary=analysis["ai_summary"],
        suggested_next_step=analysis["suggested_next_step"],
        knowledge_source=analysis["knowledge_source"],
        status="New"
    )

    db.add(matter)
    db.commit()
    db.refresh(matter)
    return matter

@app.get("/matters", response_model=list[MatterOut])
def list_matters(db: Session = Depends(get_db)):
    return db.query(Matter).order_by(Matter.id.desc()).all()

@app.get("/matters/{matter_id}", response_model=MatterOut)
def get_matter(matter_id: int, db: Session = Depends(get_db)):
    matter = db.query(Matter).filter(Matter.id == matter_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter

@app.patch("/matters/{matter_id}/status", response_model=MatterOut)
def update_matter_status(
    matter_id: int,
    payload: MatterStatusUpdate,
    db: Session = Depends(get_db)
):
    allowed = {"New", "Under Review", "Assigned", "Completed"}

    if payload.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(sorted(allowed))}"
        )

    matter = db.query(Matter).filter(Matter.id == matter_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    matter.status = payload.status
    db.commit()
    db.refresh(matter)
    return matter

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total = db.query(func.count(Matter.id)).scalar() or 0
    new_count = db.query(func.count(Matter.id)).filter(Matter.status == "New").scalar() or 0
    under_review = db.query(func.count(Matter.id)).filter(Matter.status == "Under Review").scalar() or 0
    completed = db.query(func.count(Matter.id)).filter(Matter.status == "Completed").scalar() or 0
    high = db.query(func.count(Matter.id)).filter(Matter.priority == "High").scalar() or 0

    return {
        "total": total,
        "new": new_count,
        "under_review": under_review,
        "completed": completed,
        "high_priority": high
    }
