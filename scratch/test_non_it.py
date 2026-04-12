import time
from backend.parser.llm_extractor import extract_structured_data

NON_IT_RESUME = """
Sarah Miller
sarah.m@email.com | +44 7700 900000
Address: 45 High Street, Manchester, M1 1BE, UK

SUMMARY
Dynamic Marketing Manager with 6 years of experience in digital advertising and brand strategy.

EXPERIENCE
- Marketing Lead at FashionHub (2021-Present)
  Increased organic traffic by 40% using SEO and content marketing. Managed a budget of £10k/month.
- Social Media Coordinator at TrendSetters (2018-2021)
  Grew Instagram following from 10k to 100k.

SKILLS
Google Analytics, SEO, SEM, Content Strategy, Brand Management, Adobe Creative Suite.
"""

def test_non_it_extraction():
    print(f"--- Testing Non-IT Resume Extraction ---")
    result = extract_structured_data(NON_IT_RESUME)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        import json
        print(json.dumps(result, indent=2))
        
        # Check if role and feedback are industry-appropriate
        role = result.get("identified_role", "").lower()
        feedback = result.get("market_analysis", {}).get("detailed_feedback", "").lower()
        skills = result.get("market_analysis", {}).get("missing_trending_skills", [])
        
        print(f"\nIdentified Role: {result.get('identified_role')}")
        print(f"Feedback: {result.get('market_analysis', {}).get('detailed_feedback')}")
        print(f"Missing Skills: {skills}")
        
        assert "marketing" in role
        print("\nSuccess! The parser identifies non-IT roles correctly.")

if __name__ == "__main__":
    test_non_it_extraction()
