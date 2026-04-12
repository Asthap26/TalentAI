from sqlalchemy.orm import Session
from backend.db.models import Candidate, Job, Match, CandidateSkill, JobSkill, SkillTaxonomy
from backend.db.vector_store import vector_db
import json
import time
from backend.parser.llm_extractor import llm, PROMPT_TEMPLATE # Reusing LLM setup
from langchain_core.prompts import PromptTemplate

SEARCH_PROMPT = """
Role: You are an AI Headhunter.
Task: Evaluate how well a candidate matches a specific hiring requirement.

Requirement: {query}
Candidate Skills: {skills}
Candidate Experience: {experience}

Return ONLY a JSON object with:
{{
  "score": number (0-100),
  "reasoning": "string explaining the match"
}}
"""

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

    def search_by_query(self, query: str, candidate_ids: list = None) -> list:
        if candidate_ids:
            candidates = self.db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all()
        else:
            candidates = self.db.query(Candidate).all()
            
        if not candidates: return []
        if not llm: return [{"name": f"{c.first_name}", "error": "LLM Off"} for c in candidates]

        # 1. Prepare a comprehensive skill-focused summary of ALL candidates
        candidate_summaries = []
        for i, cand in enumerate(candidates):
            skills = cand.parsed_json.get("skills", []) if cand.parsed_json else []
            summary = f"ID:{i} | Name:{cand.first_name} | TECHNICAL SKILLS: {', '.join(skills)}"
            candidate_summaries.append(summary)

        batch_prompt = f"""
        Role: Senior Technical Talent Scouter.
        Mandate: Evaluate candidates strictly based on their technical skill alignment with the following requirement.
        
        Hirer Expectation: "{query}"
        
        Candidates to Evaluate:
        {chr(10).join(candidate_summaries)}
        
        Task: 
        1. Compare candidate 'TECHNICAL SKILLS' against the 'Hirer Expectation'.
        2. Assign a score (0-100) based on skill match depth.
        3. Provide brief reasoning that focuses ONLY on which skills matched or were missing.
        
        Return ONLY a JSON list: [{{ "id": number, "score": number, "reasoning": "SKILLS MATCHED: [list]; SKILLS MISSING: [list]" }}]
        """
        
        try:
            print(f"--- Batch Evaluating {len(candidates)} candidates... ---")
            start = time.time()
            # We use direct string prompt for speed and less overhead
            response = llm.invoke(batch_prompt)
            print(f"--- Batch Search finished in {time.time() - start:.2f}s ---")
            
            raw_content = response.content if hasattr(response, 'content') else str(response)
            clean_json = raw_content[raw_content.find('['):raw_content.rfind(']')+1]
            rankings = json.loads(clean_json)
            
            results = []
            for rank in rankings:
                idx = rank.get("id")
                if idx is not None and idx < len(candidates):
                    cand = candidates[idx]
                    results.append({
                        "id": str(cand.id),
                        "name": f"{cand.first_name} {cand.last_name}",
                        "email": cand.email,
                        "score": rank.get("score", 0),
                        "reasoning": rank.get("reasoning", "")
                    })
            return sorted(results, key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            print(f"Batch Search Error: {e}")
            return []
