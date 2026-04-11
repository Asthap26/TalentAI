# Product Requirements Document (PRD): Multi-Tasking Resume Parser & Talent Intelligence System

## 1. Project Overview
The objective is to build a robust, multi-agent AI system for intelligent resume parsing and semantic candidate-job matching. This system uses advanced Natural Language Processing (NLP) and Large Language Models (LLMs) to understand the *context* of a candidate's experience, matching them to job roles based on conceptual skills rather than simple keywords. 

To meet the requirement of being **completely free**, the system will rely heavily on open-source local LLMs (Llama-3 via Ollama) instead of paid APIs like OpenAI or Anthropic.

## 2. Technology Stack
In alignment with the Problem Statement requirements and free/open-source constraints:

*   **Programming Language**: Python 3.11+
*   **Agent Orchestration**: LangGraph (for graph-based state management and multi-agent coordination)
*   **LLM Integration**: Local Llama-3 (via Ollama) mapped through LangChain.
*   **Document Parsing & NLP**:
    *   PyMuPDF (fitz) for PDF extraction.
    *   python-docx for Word document extraction.
    *   pytesseract for OCR (fallback for scanned PDFs).
    *   sentence-transformers (`all-MiniLM-L6-v2`) for vector embeddings.
*   **Databases & Data Management**:
    *   PostgreSQL (via SQLAlchemy ORM) for relational structured data.
    *   ChromaDB for the vector database (semantic similarity matching).
*   **API & Infrastructure**:
    *   FastAPI + OpenAPI/Swagger for REST endpoints.
    *   Redis + Celery for background asynchronous tasks (e.g., long PDF parsing).
    *   Docker & Docker Compose for containerization.
*   **Frontend / Observability**:
    *   Next.js (React) for a fast, modern frontend dashboard.

## 3. System Architecture & Modules

### 3.1 Document Ingestion & Parsing Module
*   **Functionality**: Accepts file uploads (PDF, DOCX) via the FastAPI backend.
*   **Process**: Detects file type, uses PyMuPDF or python-docx to extract raw text content. If the text is empty (scanned document), it routes to `pytesseract` for OCR.

### 3.2 Information Extraction Agent (LangGraph Node)
*   **Functionality**: Parses unstructured text into structured JSON.
*   **Process**: Feeds raw text to the local Llama-3 model with a strict schema prompt to extract:
    *   Personal Info (Name, Email, Phone)
    *   Education (Degree, Institution, Dates)
    *   Experience (Company, Role, Dates, Responsibilities)
    *   Skills (Technical and Soft skills).

### 3.3 Skill Taxonomy & Embedding Module
*   **Functionality**: Normalizes extracted skills.
*   **Process**: Cross-references raw extracted skills with a master `taxonomy.json`. Converts normalized skills and experience summaries into high-dimensional vectors using `sentence-transformers` and stores them in ChromaDB.

### 3.4 Job Matcher Agent (LangGraph Node)
*   **Functionality**: Scores how well a candidate fits a job description.
*   **Process**: Takes target Job Description, converts requirements to vectors. Queries ChromaDB for candidates with high cosine similarity. Asks Llama-3 to generate an **"Explainable AI Reasoning"** summary (e.g., "Candidate is an 85% match because...").

### 3.5 API and Asynchronous Workers
*   **FastAPI Engine**: Endpoints for `/upload_resume`, `/add_job`, `/match_candidates`.
*   **Celery Workers**: Resume parsing is resource-intensive. FastAPI immediately returns a `task_id` and offloads the Llama-3 processing to a Redis-backed Celery worker.

---

## 4. Sprint 1 Deliverables (Foundation & Data Setup)
As per the project blueprint, Sprint 1 focuses on generating the baseline test data and bootstrapping the foundational infrastructure. 

*   **Task 1.1**: Synthetic Resume Dataset (500+ parsed JSONs + PDF/DOCX variants).
*   **Task 1.2**: Skill Taxonomy database (`taxonomy.json`).
*   **Task 1.3**: PostgreSQL Schema (`schema.sql` with Candidates, Skills, Jobs, Matches).
*   **Task 1.4**: Docker Compose setup (`docker-compose.yml` for Postgres, Redis, ChromaDB, FastAPI).
*   **Task 1.5**: 100 Sample Job Descriptions (`jobs.json`).
