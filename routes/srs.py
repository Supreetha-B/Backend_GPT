from fastapi import APIRouter, UploadFile, File,HTTPException
from fastapi.responses import FileResponse
from services.extractor import extract_text_from_pdf
from services.llm_agent import extract_key_features_from_text, generate_code_from_features
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

# @router.post(
#         "/generate-code/",
#         summary="Generate code from extracted key features",
#         response_description="Download generated FastAPI project as .zip",
#         responses={
#             200:{
#                 "content":{"application/zip":{}},
#                 "description":"Returns a .zip file containing the generated FastAPI project"
#             }
#         },
#         response_class=FileResponse
#         )
# async def generate_code():
#     try:
#         with open("outputs/extracted_text.txt", "r",encoding="utf-8") as f:
#             text = f.read()
#         output_dir = generate_code_from_features(text)
#         os.makedirs("outputs",exist_ok=True)
#         # if not os.path.exists("output"):
#         #     os.makedirs("outputs")

#         zip_path=os.path.join("outputs,generated_code.zip")
#         zip_directory(output_dir,zip_path)

#         return FileResponse(
#             path=zip_path,
#             filename="generated_code.zip",
#             media_type="application/zip",
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500,detail=str(e))


@router.post("/generate-code/",response_class=FileResponse)
def generate_code():
    with open("outputs/key_features.txt","r") as f:
        key_features=f.read()
    project_path=generate_code_from_features(key_features)
    zip_path=zip_directory(project_path)
    return FileResponse(zip_path,media_type="application/zip",filename="generated_code.zip")