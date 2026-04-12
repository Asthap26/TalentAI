import time
from backend.parser.llm_extractor import extract_structured_data

SAMPLE_RESUME = """
Jane Smith
janesmith@email.com | +1-234-567-8900 | London, UK

SUMMARY
Versatile Software Engineer with 5 years of experience in mobile and web development.

EXPERIENCE
- Senior Engineer at MobileFirst (2021-Present)
  Developed high-performance iOS apps using Swift and SwiftUI.
- Web Developer at PixelPerfect (2019-2021)
  Built responsive web applications using Vue.js and Firebase.

SKILLS
Swift, SwiftUI, JavaScript, Vue.js, Firebase, Git, Agile.
"""

def test_extraction():
    print(f"--- Starting Extraction Test ---")
    start = time.time()
    result = extract_structured_data(SAMPLE_RESUME)
    end = time.time()
    
    print(f"\nTotal Time: {end - start:.2f}s")
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("Success! Data extracted:")
        import json
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_extraction()
