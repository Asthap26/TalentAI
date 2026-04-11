import os
import sys
import json

# Add backend to path so we can import models and db logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.session import engine, SessionLocal
from backend.db.models import Base, SkillTaxonomy, Job, Candidate
from backend.db.vector_store import vector_db

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def init_db():
    print("Creating PostgreSQL tables from schema...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

def seed_taxonomy(db):
    try:
        with open(os.path.join(DATA_DIR, "taxonomy.json"), "r") as f:
            taxonomy_data = json.load(f)
    except FileNotFoundError:
        print("taxonomy.json not found. Run generate_synthetic_data.py first.")
        return

    # Check if we already seeded
    if db.query(SkillTaxonomy).first():
        print("Taxonomy already exists in PostgreSQL. Skipping.")
        return

    print("Seeding skills into PostgreSQL...")
    db_skills = []
    vector_skills = []

    for skill in taxonomy_data:
        # Avoid id collision if we regenerate (since UUID might be string, need mapping if necessary)
        # But we let postgres auto-generate UUIDs, so we map raw JSON to rows
        new_skill = SkillTaxonomy(
            skill_name=skill["name"],
            category=skill["category"],
            is_core=skill["is_core"]
        )
        db.add(new_skill)
        db_skills.append(new_skill)
    
    db.commit()

    # Now load into ChromaDB
    print("Seeding skills into ChromaDB...")
    for sk in db_skills:
        vector_skills.append({
            "id": str(sk.id),
            "name": sk.skill_name,
            "category": sk.category
        })
    vector_db.add_skills(vector_skills)
    print(f"Successfully seeded {len(db_skills)} skills into Postgres and ChromaDB!")

def seed_jobs(db):
    try:
        with open(os.path.join(DATA_DIR, "jobs.json"), "r") as f:
            jobs_data = json.load(f)
    except FileNotFoundError:
        print("jobs.json not found. Run generate_synthetic_data.py first.")
        return

    if db.query(Job).first():
        print("Jobs already exist in PostgreSQL. Skipping.")
        return

    print("Seeding jobs into PostgreSQL...")
    for job in jobs_data:
        new_job = Job(
            title=job["title"],
            company=job["company"],
            description=job["description"],
            job_type="Full-time" # Defaulting since not in JSON
        )
        db.add(new_job)

    db.commit()
    print("Jobs successfully seeded!")

if __name__ == "__main__":
    init_db()
    
    db = SessionLocal()
    try:
        seed_taxonomy(db)
        seed_jobs(db)
        print("Sprint 1 Database Seeding Complete!")
    finally:
        db.close()
