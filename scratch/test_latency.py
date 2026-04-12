import time
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

SAMPLE_RESUME = """
John Doe
Email: john.doe@example.com
Phone: +1-555-010-999
Location: San Francisco, USA

Experience:
- Senior Software Engineer at TechCorp (2020-Present)
  Built scalable microservices using Python and Go. Led a team of 5 engineers.
- Software Developer at WebSoft (2018-2020)
  Developed frontend features using React and Redux.

Skills: Python, Go, React, AWS, Docker, Kubernetes.
"""

PROMPT_TEMPLATE = """
Role: You are an Expert Talent Acquisition Specialist.
Task: Parse this resume and return JSON.

Desired JSON Schema:
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "identified_role": "string",
  "skills": ["string"],
  "experience": [{{ "company": "string", "role": "string", "duration": "string" }}],
  "market_analysis": {{
    "score": number,
    "role_context": "string",
    "detailed_feedback": "string",
    "missing_trending_skills": ["string"]
  }}
}}

Resume: {text}
"""

def test_model(model_name):
    print(f"\n--- Testing Model: {model_name} ---")
    try:
        llm = ChatOllama(model=model_name, temperature=0, format="json")
        start = time.time()
        prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
        chain = prompt | llm
        response = chain.invoke({"text": SAMPLE_RESUME})
        end = time.time()
        print(f"Time taken: {end - start:.2f}s")
        print(f"Response: {response.content[:100]}...")
        return end - start
    except Exception as e:
        print(f"Error testing {model_name}: {e}")
        return None

if __name__ == "__main__":
    t_8b = test_model("llama3:latest")
    t_1b = test_model("llama3.2:1b")
    
    if t_8b and t_1b:
        print(f"\nSpeedup: {t_8b / t_1b:.2f}x")
