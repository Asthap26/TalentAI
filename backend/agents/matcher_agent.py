from sqlalchemy.orm import Session
from backend.db.models import Candidate, Job, Match, CandidateSkill, JobSkill, SkillTaxonomy
from backend.db.vector_store import vector_db
import json

class MatcherAgent:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def calculate_match(self, candidate_id: str, job_id: str) -> dict:
        candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        job = self.db.query(Job).filter(Job.id == job_id).first()
        
        if not candidate or not job:
            raise ValueError("Candidate or Job not found")
            
        # 1. Get parsed skills from candidate and job requirements
        # For simplicity, if skills relationships aren't populated, we grab from parsed_json
        cand_skills = []
        if candidate.parsed_json and "skills" in candidate.parsed_json:
            cand_skills = candidate.parsed_json["skills"]
            
        # Get Job requirements
        job_reqs = self.db.query(JobSkill).filter(JobSkill.job_id == job_id).all()
        required_skills = []
        for req in job_reqs:
            sk = self.db.query(SkillTaxonomy).filter(SkillTaxonomy.id == req.skill_id).first()
            if sk:
                required_skills.append(sk.skill_name)
                
        # 2. Heuristic Scoring
        if not required_skills:
            score = 0.5 # Default middle score if no reqs
            reasoning = "Job has no specific skills listed."
        else:
            match_count = 0
            cand_skills_lower = [s.lower() for s in cand_skills]
            matched_skills = []
            missing_skills = []
            
            for req in required_skills:
                # Direct match
                if req.lower() in cand_skills_lower:
                    match_count += 1
                    matched_skills.append(req)
                else:
                    # Semantic search backstop utilizing ChromaDB
                    semantic_matches = vector_db.search_canonical_skill(req, top_k=1)
                    found_semantic = False
                    if semantic_matches:
                        for sm in semantic_matches:
                            if sm['distance'] < 0.3 and sm['name'].lower() in cand_skills_lower:
                                match_count += 1
                                matched_skills.append(f"{req} (Matched via {sm['name']})")
                                found_semantic = True
                                break
                    if not found_semantic:
                        missing_skills.append(req)
                    
            score = match_count / len(required_skills)
            reasoning = f"Matched exactly on {len(matched_skills)}/{len(required_skills)} required skills. Missing: {', '.join(missing_skills) if missing_skills else 'None'}."

        # 3. Output payload
        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "score": round(score, 4),
            "reasoning": reasoning,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        }
