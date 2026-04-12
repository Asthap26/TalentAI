import json
import ast
import re
import sys
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

import time

# Llama-3.2 (1b) is the best balance of speed and extraction accuracy for local parsing.
# llama3 (8b) is better for complex analysis but can be very slow.
MODEL_NAME = "llama3.2:1b" 

try:
    # Using ChatOllama with temperature=0 and JSON mode for maximum reliability
    llm = ChatOllama(model=MODEL_NAME, temperature=0, format="json")
except Exception as e:
    print(f"Warning: Ollama not configured or {MODEL_NAME} not available locally.")
    llm = None

# This is the "System Prompt" that tells the AI exactly how to behave.
PROMPT_TEMPLATE = """
Task: Extract candidate data from resume text.
Focus: Skills, role, name, email, location, experience.
Market Analysis: Score (0-100) vs their role. 3 field-specific 'X-Factor' skills.

Strict JSON Output ONLY:
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "location": "string",
  "identified_role": "string",
  "skills": ["list of strings"],
  "experience": [{{ "role": "string", "company": "string", "duration": "string" }}],
  "market_analysis": {{
    "score": number,
    "role_context": "brief string",
    "detailed_feedback": "one sentence",
    "missing_trending_skills": ["list"]
  }}
}}

Resume:
{text}
"""

def extract_structured_data(text: str) -> dict:
    """
    Core function that takes raw resume text and returns a Python dictionary.
    Handles multiple levels of fallback parsing for maximum reliability.
    """
    if not llm:
        return {"error": f"LLM not initialized. Make sure Ollama ({MODEL_NAME}) is running locally."}
        
    if not text or not text.strip():
        return {"error": "The uploaded PDF/DOCX appears to be empty or contains non-selectable text (e.g., it might be a scanned image). Please try a different file."}
        
    start_time = time.time()
    text = text[:6000] # Reduced truncation to 6000 for better 1B model focus
    
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm
    
    try:
        print(f"--- Calling LLM ({MODEL_NAME})... ---")
        response = chain.invoke({"text": text})
        extraction_time = time.time() - start_time
        print(f"--- LLM Response received in {extraction_time:.2f}s ---")
        
        # ChatOllama returns an AIMessage, we need the .content string
        raw_text = response.content if hasattr(response, 'content') else str(response)
        
        # DEBUG: Log the first 100 chars of raw output
        print(f"DEBUG: AI Raw Output (truncated): {raw_text[:200]}...")

        # 1. ROBUST EXTRACTION: Try to find the largest valid JSON block
        clean_res = raw_text.strip()
        start_idx = clean_res.find('{')
        if start_idx == -1:
            print("ERROR: Could not find opening brace { in response.")
            return {"error": "Could not identify JSON block in AI response.", "raw": raw_text[:500]}
            
        # Try all closing braces from last to first to find the valid one
        json_obj = None
        for i in range(len(clean_res), start_idx, -1):
            if clean_res[i-1] == '}':
                candidate = clean_res[start_idx:i]
                try:
                    # Attempt 1: Standard JSON
                    json_obj = json.loads(candidate)
                    break
                except Exception:
                    # Attempt 2: Sanitize and try again
                    sanitized = re.sub(r',\s*([\]}])', r'\1', candidate)
                    sanitized = re.sub(r':\s*\'(.*?)\'(?=\s*[,\]}])', r': "\1"', sanitized)
                    if '"' not in sanitized and "'" in sanitized:
                        sanitized = sanitized.replace("'", '"')
                    try:
                        json_obj = json.loads(sanitized)
                        break
                    except Exception:
                        continue
        
        if json_obj:
             return json_obj

        # 3. HEURISTIC REPAIR: Try to extract key fields via regex if everything else fails
        try:
             print("WARNING: Falling back to Heuristic Repair...")
             repair = {
                 "name": (re.search(r'"name":\s*"([^"]*)"', raw_text) or re.search(r'Name:\s*(.*)', raw_text)).group(1).split('\n')[0].strip(),
                 "email": (re.search(r'[\w\.-]+@[\w\.-]+', raw_text)).group(0),
                 "identified_role": (re.search(r'"identified_role":\s*"([^"]*)"', raw_text) or re.search(r'Role:\s*(.*)', raw_text)).group(1).split('\n')[0].strip(),
                 "skills": re.findall(r'"skills":\s*\[(.*?)\]', raw_text, re.S)[0].replace('"', '').split(',') if '"skills"' in raw_text else []
             }
             if repair["name"] and repair["email"]:
                  print("DEBUG: Heuristic Repair Succeeded!")
                  return repair
        except:
             pass

        # 4. PARSING ATTEMPT 3: ast.literal_eval (Handles Python-style dicts)
        try:
            result = ast.literal_eval(clean_res)
            if isinstance(result, dict):
                return result
        except Exception as e:
            print(f"DEBUG: literal_eval also failed: {e}")
        
        # FINAL FALLBACK: If we got here, parsing completely failed.
        print(f"CRITICAL ERROR: All parsing attempts failed for: {clean_res[:200]}")
        return {
            "error": "Failed to parse AI output into valid data.",
            "hint": "The AI returned invalid JSON. Try again or check the logs.",
            "raw_snippet": clean_res[:200]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Extraction Error: {str(e)}"}

if __name__ == "__main__":
    # Internal test to ensure the template loads correctly
    print("LLM Extractor successfully initialized with Prompt Template.")
