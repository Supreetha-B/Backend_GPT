from utils.pdf_parser import parse_pdf
import os

async def extract_text_from_pdf(file):
    content = await file.read()
    extracted_text = parse_pdf(content)
    os.makedirs("outputs",exist_ok=True)
    with open("outputs/extracted_text.txt", "w",encoding="utf-8") as f:
        f.write(extracted_text)
    return extracted_text