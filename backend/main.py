import os
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from backend.db.session import get_db, Base, engine
from backend.db.models import Candidate, Job, Match, CandidateSkill, SkillTaxonomy, JobSkill
from backend.agents.matcher_agent import MatcherAgent
from backend.parser.pdf_parser import extract_text_from_pdf
from backend.parser.docx_parser import extract_text_from_docx
from backend.parser.llm_extractor import extract_structured_data

# Ensure tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Talent Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Talent Intelligence API. System is live!"}

@app.get("/jobs")
def get_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return [{"id": str(j.id), "title": j.title, "company": j.company} for j in jobs]

@app.get("/candidates")
def get_candidates(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    candidates = db.query(Candidate).offset(skip).limit(limit).all()
    return [{"id": str(c.id), "name": f"{c.first_name} {c.last_name}", "email": c.email} for c in candidates]

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Save file temporarily
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    # 2. Extract Text
    text = ""
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
        
    os.remove(file_path)
    
    # 3. Parse with LLM
    parsed = extract_structured_data(text)
    if "error" in parsed:
        raise HTTPException(status_code=500, detail=parsed["error"])
        
    # 4. Save to Database
    name_parts = parsed.get("name", "Unknown Person").split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    # Check if candidate exists
    candidate = db.query(Candidate).filter(Candidate.email == parsed.get("email")).first()
    if not candidate:
        candidate = Candidate(
            first_name=first_name,
            last_name=last_name,
            email=parsed.get("email", f"{first_name}@example.com"),
            phone=parsed.get("phone", ""),
            raw_resume_text=text,
            parsed_json=parsed
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    return {"message": "Resume processed successfully", "candidate_id": str(candidate.id), "parsed_data": parsed}

@app.get("/match/{candidate_id}/{job_id}")
def match_candidate_job(candidate_id: str, job_id: str, db: Session = Depends(get_db)):
    agent = MatcherAgent(db)
    try:
        result = agent.calculate_match(candidate_id, job_id)
        
        # Save Match to Database
        match_record = db.query(Match).filter(Match.candidate_id == candidate_id, Match.job_id == job_id).first()
        if not match_record:
            match_record = Match(
                job_id=job_id,
                candidate_id=candidate_id,
                match_score=result["score"],
                explainable_reasoning=result["reasoning"]
            )
            db.add(match_record)
            db.commit()
            
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
