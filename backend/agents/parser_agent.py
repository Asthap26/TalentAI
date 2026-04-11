import os
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Define the structured output schema strictly using Pydantic
class ExperienceNode(BaseModel):
    company: str = Field(description="Name of the company")
    role: str = Field(description="The job title or role")
    duration: str = Field(description="The time period worked (e.g., 'Jan 2020 - Present')")
    description: str = Field(description="A brief summary of responsibilities and achievements")

class EducationNode(BaseModel):
    institution: str = Field(description="Name of the university or school")
    degree: str = Field(description="Degree obtained (e.g., 'Bachelor of Science in Computer Science')")
    year: str = Field(description="Graduation year or time period")

class ParsedResume(BaseModel):
    name: str = Field(description="Full name of the candidate. Return 'Unknown' if not clearly stated.")
    email: str = Field(description="Candidate's email address")
    phone: str = Field(description="Candidate's phone number")
    skills: list[str] = Field(description="A flat list of all technical and soft skills explicitly mentioned.")
    experience: list[ExperienceNode] = Field(description="List of all work experiences.")
    education: list[EducationNode] = Field(description="List of all educational backgrounds.")

class ResumeParserAgent:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initializes the agent with an OpenAI LLM configured for Structured Output.
        Requires OPENAI_API_KEY to be set in the .env file.
        """
        # Ensure your OPENAI_API_KEY is available in the environment
        if not os.getenv("OPENAI_API_KEY"):
            print("WARNING: OPENAI_API_KEY not found. Agent will fail if called.")
            
        self.llm = ChatOpenAI(model=model_name, temperature=0.0)
        
        # Use LangChain's structured output wrapper
        self.structured_llm = self.llm.with_structured_output(ParsedResume)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert HR Talent Intelligence AI. Your task is to extract highly accurate, structured information from a candidate's resume text. Handle inconsistent layouts gracefully and infer missing structured fields cautiously. If you cannot find a piece of information, omit it or use 'Unknown' as appropriate."),
            ("human", "Here is the raw, unstructured resume text. Please parse it:\n\n{resume_text}")
        ])
        
        self.chain = self.prompt | self.structured_llm

    def parse(self, raw_text: str) -> dict:
        """
        Executes the extraction chain on raw resume text.
        Returns a dictionary representing the ParsedResume schema.
        """
        if not raw_text or len(raw_text.strip()) < 50:
            raise ValueError("Input text is too short or empty to be a valid resume.")
            
        try:
            print("Sending resume text to LLM for parsing...")
            result: ParsedResume = self.chain.invoke({"resume_text": raw_text})
            # Convert Pydantic object back to dict for easy storage in JSONB
            return result.model_dump()
        except Exception as e:
            print(f"Error during LLM parsing: {e}")
            raise e

if __name__ == "__main__":
    # Small test script
    sample_text = """
    Alice Johnson
    Email: alice.dev@example.com
    Phone: 555-0199
    
    Skills: Python, Django, React, AWS, Docker
    
    Work Experience:
    Senior Engineer at TechCorp
    Jan 2021 - Present
    - Built microservices using Python and Docker.
    - Led a team of 3 developers.
    
    Education:
    B.S. Computer Science, University of State
    Graduated: 2020
    """
    
    # Needs valid OPENAI_API_KEY to run
    if os.getenv("OPENAI_API_KEY"):
        agent = ResumeParserAgent()
        out = agent.parse(sample_text)
        print("Parsed Output Successfully!")
        import json
        print(json.dumps(out, indent=2))
    else:
        print("Set OPENAI_API_KEY to test the ParserAgent.")
