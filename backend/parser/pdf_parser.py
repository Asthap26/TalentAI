import fitz  # PyMuPDF

def extract_text_from_pdf(filepath: str) -> str:
    """
    Extracts text from a PDF using PyMuPDF (extremely fast).
    Returns the accumulated text string.
    """
    text = ""
    try:
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
    return text

if __name__ == "__main__":
    # Test section
    print("PDF Parser (PyMuPDF) initialized.")
