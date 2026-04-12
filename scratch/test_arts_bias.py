import time
from backend.parser.llm_extractor import extract_structured_data

ARTS_RESUME = """
Analyn Ocampo
aocampo@ucdavis.edu | (559) 555-5683
Davis, CA 95616

EDUCATION
Bachelor of Arts in Communications, UC Davis (2023)

EXPERIENCE
- Receptionist at T & T Electronics (June 2023 - August 2023)
  Handled customer inquiries and managed scheduling.
- Child Care Provider (Self Employed) (June 2021 - September 2023)
  Managed schedules and activities for children.

SKILLS
Communication, Customer Service, Organizational Skills, Time Management.
"""

def test_arts_resume():
    print(f"--- Testing Bachelor of Arts Resume ---")
    result = extract_structured_data(ARTS_RESUME)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        import json
        print(json.dumps(result, indent=2))
        
        feedback = result.get("market_analysis", {}).get("detailed_feedback", "").lower()
        skills = result.get("market_analysis", {}).get("missing_trending_skills", [])
        
        print(f"\nFeedback: {result.get('market_analysis', {}).get('detailed_feedback')}")
        print(f"X-Factors: {skills}")
        
        # Verify NO IT bias
        it_keywords = ["cloud", "coding", "software", "it industry", "data analysis", "developer"]
        found_it_bias = any(kw in feedback for kw in it_keywords) or any(kw in "".join(skills).lower() for kw in it_keywords)
        
        if found_it_bias:
            print("\nFAILURE: Detected IT bias in a non-IT resume analysis.")
        else:
            print("\nSUCCESS: No IT bias detected. The analysis is industry-appropriate.")

if __name__ == "__main__":
    test_arts_resume()
