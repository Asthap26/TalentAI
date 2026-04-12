import time
from backend.parser.llm_extractor import extract_structured_data

SAMPLE_RESUME_PRECISE = """
Alice Johnson
alice.j@example.com | +1-555-0123
Address: 123 Tech Lane, Austin, TX 78701, USA

SUMMARY
DevOps Engineer with 3 years of experience.

EXPERIENCE
- Cloud Engineer at Starlink (2022-Present)
  Managing AWS infrastructure.
"""

def test_precise_location():
    print(f"--- Testing Precise Location Extraction ---")
    result = extract_structured_data(SAMPLE_RESUME_PRECISE)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Extracted Location: {result.get('location')}")
        assert "TX" in result.get('location') or "Austin" in result.get('location')
        print("Success!")

if __name__ == "__main__":
    test_precise_location()
