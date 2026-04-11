import os
import json
import random
from faker import Faker
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

faker = Faker()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RESUMES_DIR = os.path.join(DATA_DIR, "resumes")
os.makedirs(RESUMES_DIR, exist_ok=True)

# 1. Generate Taxonomy
def generate_taxonomy():
    categories = {
        "Software Engineering": ["Python", "Java", "Docker", "AWS", "React", "Node.js", "Kubernetes", "SQL", "Git"],
        "Data Science": ["Machine Learning", "Python", "R", "SQL", "Pandas", "Scikit", "TensorFlow", "Statistics"],
        "Product Management": ["Agile", "Scrum", "Jira", "Roadmapping", "A/B Testing", "User Research", "Strategy"],
        "Design": ["Figma", "UI/UX", "Adobe Creative Suite", "Prototyping", "Wireframing", "User Research"]
    }
    
    taxonomy = []
    skill_id = 1
    for category, skills in categories.items():
        for skill in skills:
            taxonomy.append({
                "id": f"sk-{skill_id}",
                "name": skill,
                "category": category,
                "is_core": True
            })
            skill_id += 1
            
    with open(os.path.join(DATA_DIR, "taxonomy.json"), "w") as f:
        json.dump(taxonomy, f, indent=4)
    print(f"Generated taxonomy.json with {len(taxonomy)} skills.")
    return taxonomy

# 2. Generate Jobs
def generate_jobs(taxonomy, count=100):
    jobs = []
    categories = list(set([t["category"] for t in taxonomy]))
    
    for i in range(count):
        cat = random.choice(categories)
        relevant_skills = [s["name"] for s in taxonomy if s["category"] == cat]
        
        job = {
            "id": f"job-{i+1}",
            "title": f"Senior {cat} Role",
            "company": faker.company(),
            "description": faker.text(max_nb_chars=500),
            "required_skills": random.sample(relevant_skills, min(len(relevant_skills), random.randint(3, 6)))
        }
        jobs.append(job)
        
    with open(os.path.join(DATA_DIR, "jobs.json"), "w") as f:
        json.dump(jobs, f, indent=4)
    print(f"Generated jobs.json with {count} roles.")

def create_pdf(text, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    textobject = c.beginText()
    textobject.setTextOrigin(50, 750)
    textobject.setFont("Helvetica", 11)
    
    for line in text.split('\n'):
        textobject.textLine(line)
    
    c.drawText(textobject)
    c.save()

def create_docx(text, filename):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)

# 3. Generate Resumes
def generate_resumes(taxonomy, count=500):
    all_skills = [t["name"] for t in taxonomy]
    resumes_json = []

    for i in range(count):
        name = faker.name()
        email = faker.email()
        phone = faker.phone_number()
        skills = random.sample(all_skills, random.randint(4, 10))
        experience = faker.text(max_nb_chars=300)
        
        resume_text = f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nExperience:\n{experience}\n\nSkills:\n{', '.join(skills)}"
        
        resume_data = {
            "id": f"res-{i+1}",
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "raw_text": resume_text
        }
        resumes_json.append(resume_data)

        # Decide format randomly
        format_type = random.choice(["pdf", "docx"])
        filename = os.path.join(RESUMES_DIR, f"candidate_{i+1}.{format_type}")
        
        if format_type == "pdf":
            create_pdf(resume_text, filename)
        else:
            create_docx(resume_text, filename)
            
    with open(os.path.join(RESUMES_DIR, "resumes.json"), "w") as f:
        json.dump(resumes_json, f, indent=4)
    print(f"Generated {count} resumes in {RESUMES_DIR}")

if __name__ == "__main__":
    print("Starting synthetic data generation for Sprint 1...")
    tax = generate_taxonomy()
    generate_jobs(tax, count=100)
    generate_resumes(tax, count=500)
    print("Sprint 1 Data Generation Complete!")
