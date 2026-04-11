from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
import json

# Setup local Llama-3 model using Ollama
# Ensure Ollama is running and Llama-3 is pulled: `ollama run llama3`
try:
    llm = Ollama(model="llama3")
except Exception as e:
    print("Warning: Ollama not configured or Llama-3 not available.")
    llm = None

PROMPT_TEMPLATE = """
You are an expert resume parser. Extract the following information from the resume text below and output ONLY a valid JSON object.
Do not include any explanation, preamble, or markdown formatting around the JSON.

Expected JSON schema:
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "skills": ["string"],
  "experience": [
    {{
      "company": "string",
      "role": "string",
      "duration": "string"
    }}
  ]
}}

Resume Text:
{text}
"""

def extract_structured_data(text: str) -> dict:
    """
    Uses the strictly formatted few-shot prompt template to extract JSON from raw text.
    """
    if not llm:
        return {"error": "LLM not initialized. Make sure Ollama (llama3) is running locally."}
        
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"text": text})
        
        # Clean up output just in case the model adds markdown codeblocks
        clean_res = response.strip()
        if clean_res.startswith("```json"):
            clean_res = clean_res[7:]
        elif clean_res.startswith("```"):
            clean_res = clean_res[3:]
            
        if clean_res.endswith("```"):
            clean_res = clean_res[:-3]
            
        result = json.loads(clean_res.strip())
        return result
    except json.JSONDecodeError:
        print("Failed to decode JSON from LLM response.")
        return {"error": "JSON parse error", "raw_response": str(response)}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("LLM Extractor loaded Template.")
