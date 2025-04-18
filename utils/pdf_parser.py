import fitz  # PyMuPDF
from io import BytesIO

def parse_pdf(pdf_bytes:bytes)->str:
    try:

        pdf_stream=BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error Parsing PDF")