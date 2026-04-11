import re
import spacy

# Ensure the spaCy model is downloaded before running in production:
# python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy model 'en_core_web_sm' not found. Please install it.")

def detect_sections(text: str) -> dict:
    """
    Detects boundaries of sections like Experience, Education, Skills.
    Uses regex and basic NLP techniques to segment the resume.
    """
    sections = {
        "personal_info": "",
        "experience": "",
        "education": "",
        "skills": "",
        "other": ""
    }
    
    current_section = "personal_info"
    lines = text.split("\n")
    
    # Heuristics for detecting section headers
    experience_keywords = ["experience", "employment", "work history", "professional experience"]
    education_keywords = ["education", "academic background", "degrees"]
    skills_keywords = ["skills", "technical skills", "core competencies", "technologies"]
    
    for line in lines:
        cleaned_line = line.strip().lower()
        if not cleaned_line:
            continue
            
        # A header is usually short and contains keywords
        if len(cleaned_line) < 40:
            if any(cleaned_line.startswith(kw) or cleaned_line.endswith(kw) for kw in experience_keywords):
                current_section = "experience"
                continue
            elif any(cleaned_line.startswith(kw) or cleaned_line.endswith(kw) for kw in education_keywords):
                current_section = "education"
                continue
            elif any(cleaned_line.startswith(kw) or cleaned_line.endswith(kw) for kw in skills_keywords):
                current_section = "skills"
                continue
            
        sections[current_section] += line + "\n"
        
    return sections

if __name__ == "__main__":
    sample_text = "John Doe\nSoftware Engineer\nExperience\nWorked at Google\nEducation\nMIT"
    print(detect_sections(sample_text))
