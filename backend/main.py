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

# Initialize FastAPI app with a descriptive title
app = FastAPI(title="Talent Intelligence API", version="1.0.0")

# CORS (Cross-Origin Resource Sharing) middleware
# This allows your Next.js frontend (on port 3000) to talk to this backend (on port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In a live app, you would restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check endpoint
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

# Main Endpoint: Upload and process a resume
@app.post("/upload-resume")
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    import time
    overall_start = time.time()
    
    # 1. Save file temporarily
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
        
    # 2. Convert File to Plain Text based on extension
    text = ""
    extract_start = time.time()
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        os.remove(file_path) # Clean up if format is unsupported
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
    
    extract_time = time.time() - extract_start
    print(f"DEBUG: Text extraction took {extract_time:.4f} seconds.")
        
    os.remove(file_path) # Delete the temp file after reading its text
    
    # 3. Brain Work: Send the text to Llama-3 for intelligent extraction
    parse_start = time.time()
    parsed = extract_structured_data(text)
    parse_time = time.time() - parse_start
    print(f"DEBUG: LLM extraction took {parse_time:.4f} seconds.")

    if "error" in parsed:
        raise HTTPException(status_code=500, detail=parsed["error"])
    
    print(f"DEBUG: Total resume processing time: {time.time() - overall_start:.4f} seconds.")
        
    # 4. Database Integration: Save the parsed candidate info
    try:
        # Deeply safeguard against null/missing values from the AI
        raw_name = parsed.get("name") or "Unknown Candidate"
        name_parts = raw_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        email = parsed.get("email") or f"pending_{int(time.time())}@example.com"
        phone = parsed.get("phone") or ""

        # Check if this email already exists so we don't create duplicates
        candidate = db.query(Candidate).filter(Candidate.email == email).first()
        if not candidate:
            candidate = Candidate(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                raw_resume_text=text,
                parsed_json=parsed # Store the full AI output as a JSON blob
            )
            db.add(candidate)
            db.commit()
            db.refresh(candidate)

        # Return the success message and the data back to the frontend
        return {"message": "Resume processed successfully", "candidate_id": str(candidate.id), "parsed_data": parsed}

    except Exception as db_err:
        import traceback
        print("CRITICAL DATABASE/LOGIC ERROR:")
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Data Processing Error: {str(db_err)}")

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

@app.get("/search-candidates")
def search_candidates(query: str, ids: str = None, db: Session = Depends(get_db)):
    agent = MatcherAgent(db)
    id_list = ids.split(",") if ids else None
    results = agent.search_by_query(query, candidate_ids=id_list)
    return results
