import pdfplumber

def extract_text_from_pdf(filepath: str) -> str:
    """
    Extracts text from a multi-column and creative layout PDF.
    Returns the accumulated text string.
    """
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                # Use layout-aware extraction to handle multi-column formats better
                page_text = page.extract_text(layout=True)
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
    return text

if __name__ == "__main__":
    # Test section
    print("PDF Parser initialized.")
