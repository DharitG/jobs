import io
from PyPDF2 import PdfReader
from fastapi import UploadFile

def parse_pdf_to_text(file: UploadFile) -> str:
    """Parses the text content from an uploaded PDF file."""
    try:
        # Read the file content into memory
        pdf_content = file.file.read() 
        # Reset file pointer just in case it's used elsewhere (good practice)
        file.file.seek(0)
        
        # Use PyPDF2 to read the PDF from the in-memory bytes
        reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or "" # Add empty string if extraction fails for a page
        return text
    except Exception as e:
        # Handle exceptions (e.g., corrupted PDF, library errors)
        print(f"Error parsing PDF {file.filename}: {e}")
        # Re-raise or return an error indicator as needed
        raise ValueError(f"Could not parse PDF file: {file.filename}") from e 