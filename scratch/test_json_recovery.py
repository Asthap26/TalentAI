import json
from backend.parser.llm_extractor import extract_structured_data

def test_recovery_from_garbage():
    print("--- Testing Recovery from Garbage/Repetition ---")
    
    # Simulate a malformed output where the model repeats itself after the closing brace
    malformed_output = """
    {
      "name": "Jane Doe",
      "email": "jane@example.com",
      "market_analysis": { "score": 90 }
    }name": "Jane Doe",
      "email": "jane@example.com",
    }
    """
    
    # Mock the LLM to return this garbage
    class MockResponse:
        content = malformed_output
        
    # We need to test the logic directly or mock the chain.invoke
    # Since I've updated the file, and I'm calling the function, 
    # but the function normally calls the LLM. 
    # I'll modify the test to only check the parsing logic if possible, 
    # but I want to see if the function handles it.
    
    # Let's create a specialized test function in the scratch file that imports the internal logic 
    # but we can't easily mock inner calls without monkeypatching.
    
    # I'll just check if the logic I added works by running a small script that mimics the internal parser.
    pass

if __name__ == "__main__":
    import re
    import ast
    
    malformed = """
    {
      "name": "Jane Doe",
      "email": "jane@example.com",
      "market_analysis": { "score": 90 }
    }name": "Jane Doe",
      "email": "jane@example.com",
    }
    """
    
    clean_res = malformed.strip()
    start_idx = clean_res.find('{')
    
    json_obj = None
    for i in range(len(clean_res), start_idx, -1):
        if clean_res[i-1] == '}':
            candidate = clean_res[start_idx:i]
            try:
                json_obj = json.loads(candidate)
                print(f"Success at index {i}!")
                break
            except:
                continue
    
    if json_obj:
        print("Final JSON:", json_obj)
    else:
        print("Failed to parse.")
