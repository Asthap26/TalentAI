import uuid
from sqlalchemy import Column, String, Text, Boolean, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .session import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    raw_resume_text = Column(Text)
    parsed_json = Column(JSONB)

    skills = relationship("CandidateSkill", back_populates="candidate")
    matches = relationship("Match", back_populates="candidate")

class SkillTaxonomy(Base):
    __tablename__ = "skills_taxonomy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100))
    is_core = Column(Boolean, default=False)

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills_taxonomy.id", ondelete="CASCADE"), primary_key=True)
    years_experience = Column(Numeric(4, 2))

    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("SkillTaxonomy")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    job_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    skills = relationship("JobSkill", back_populates="job")
    matches = relationship("Match", back_populates="job")

class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills_taxonomy.id", ondelete="CASCADE"), primary_key=True)
    is_mandatory = Column(Boolean, default=True)

    job = relationship("Job", back_populates="skills")
    skill = relationship("SkillTaxonomy")

class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    match_score = Column(Numeric(5, 4))
    explainable_reasoning = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="matches")
    candidate = relationship("Candidate", back_populates="matches")
