-- schema.sql
-- DDL for Candidates, Skills, Jobs, and Matches tables

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Candidates Table
CREATE TABLE IF NOT EXISTS candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    raw_resume_text TEXT,
    parsed_json JSONB
);

-- Taxonomy / Skills Table
CREATE TABLE IF NOT EXISTS skills_taxonomy (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100),
    is_core BOOLEAN DEFAULT false
);

-- Candidate Skills Many-to-Many
CREATE TABLE IF NOT EXISTS candidate_skills (
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills_taxonomy(id) ON DELETE CASCADE,
    years_experience NUMERIC(4, 2),
    PRIMARY KEY (candidate_id, skill_id)
);

-- Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    job_type VARCHAR(50), -- e.g., Full-time, Contract, Remote
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Job Skills Required Many-to-Many
CREATE TABLE IF NOT EXISTS job_skills (
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills_taxonomy(id) ON DELETE CASCADE,
    is_mandatory BOOLEAN DEFAULT true,
    PRIMARY KEY (job_id, skill_id)
);

-- Matches Table (To store evaluation results and AI explainability)
CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    match_score NUMERIC(5, 4), -- e.g. 0.8500
    explainable_reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, candidate_id)
);
