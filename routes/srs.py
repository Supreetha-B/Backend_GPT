from fastapi import APIRouter, UploadFile, File,HTTPException
from fastapi.responses import FileResponse
from services.extractor import extract_text_from_pdf
from services.llm_agent import extract_key_features_from_text, generate_code_from_features,generate_documentation
from utils.zipper import zip_directory
import os
router = APIRouter()

@router.post("/upload/")
async def upload_srs(file: UploadFile = File(...)):
    try:
        extracted_text = await extract_text_from_pdf(file)
        return {"extracted_text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.post("/extract-key-features/")
async def extract_key_features():
    with open("outputs/extracted_text.txt", "r",encoding="utf-8") as f:
        extracted_text = f.read()
    key_features = extract_key_features_from_text(extracted_text)
    with open("outputs/key_features.txt", "w") as f:
        f.write(key_features)
    return {"key_features": key_features}

@router.post("/generate-code/",response_class=FileResponse)
def generate_code():
    with open("outputs/key_features.txt","r") as f:
        key_features=f.read()
    project_path=generate_code_from_features(key_features)
    zip_path=zip_directory(project_path)
    return FileResponse(zip_path,media_type="application/zip",filename="generated_code.zip")

@router.post("/generate-docs/")
def generate_docs():
    message=generate_documentation()
    return {"message":message}


@router.get("/download/apidocs/")
def generate_api_doc():
    filepath="generated_code/API_DOCUMENTATION.md"
    return FileResponse(filepath,media_type="text/markdown",filename="API_DOCUMENTATION.md")

@router.get("/download/readme/")
def generate_readme():
    filepath="generated_code/README.md"
    return FileResponse(filepath,media_type="text/markdown",filename="README.md")
