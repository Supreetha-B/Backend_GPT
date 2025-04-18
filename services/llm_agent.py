import os
import requests
import json
import re
# from dotenv import load_dotenv
# from groq import Groq
# load_dotenv()
from zipfile import ZipFile

# Groq API key and endpoint setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL="llama3-70b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def groq_request(payload):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
   
    if response.status_code != 200:
        raise Exception(f"Groq API error: {response.status_code} - {response.text}")
   
    return response.json()

def extract_key_features_from_text(text):
    prompt = f"""
You are a software analyst. Extract the following from the given SRS:
- Project Purpose
- Functional Requirements
- Non-Functional Requirements
- System Modules
- User Roles
- Inputs/Outputs
- Constraints or Assumptions

SRS Document:
{text}
"""

    payload = {
        "model": "llama3-70b-8192",  # Use the Groq LLaMA model
        "messages": [
            {"role": "system", "content": "You are an expert software analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2048
    }

    response = groq_request(payload)
    return response['choices'][0]['message']['content']


def generate_code_from_text(text):
    prompt = (f"Based on the following software requirements, generate a complete FastAPI backend project structure with models, routes, and services:\n\n{text}"
              "Please format your output with code as file path like:\n"
             "# File: app/api/routes/user.py\n```python\n<code>\n```")

    payload = {
        "model": "llama3-70b-8192",  # Groq LLaMA model
        "messages": [
            {"role": "system", "content": "You are a senior Python backend engineer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 4096
    }

    response = groq_request(payload)
    generated_code = response['choices'][0]['message']['content']
   
    # Save the generated code to the `generated_code` folder
    os.makedirs("outputs/generated_code", exist_ok=True)
    with open("outputs/generated_code/main.py", "w") as f:
        f.write(generated_code)

    return generated_code

def call_groq_llama(prompt:str)->dict:
    url="https://api.groq.com/openai/v1/chat/completions"
    headers={
        "Authorization":f"Bearer {GROQ_API_KEY}",
        "Content-Type":"application/json"
    }
    payload={
        "model":GROQ_MODEL,
        "messages":[{"role":"user","content":prompt}],
        "temperature":0.3
    }
    response=requests.post(url,headers=headers,json=payload)
    if response.status_code!=200:
        raise Exception(f"Groq API Error")
    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Failed to decode json")

def generate_code_from_features(features_text:str)->str:
    base_dir="temp_output/generated_code"

    #if there is already outputs folder present it deletes
    if os.path.exists(base_dir):
        import shutil
        shutil.rmtree(base_dir)

    os.makedirs(base_dir,exist_ok=True)

    structure={
        "app/api/routes":["user.py","item.py","__init__.py"],
        "app/models":["user.py","item.py","__init__.py"],
        "app/services":["database.py"],
        "app":["main.py"],
        "tests":[],
        ".":["Dockerfile","requirements.txt",".env","README.md"]
    }

    file_contents={
        "user.py":"# user route/model\n",
        "item.py":"# item route/model\n",
        "__init__.py":"",
        "database.py":"# database setup\n",
        "main.py":'from fastapi import FastAPI\n\napp=FastAPI()\n\n@app.get("/")\ndef root():\n return {"message":"Working"}\n',
        "Dockerfile":'FROM python:3.11\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]\n',
        "requirements.txt":"fastapi\nuvicorn\nsqlalchemy\npydantic\n",
        ".env":"DATABASE_URL=postgresql://user:password@localhost/dbname\n",
        "README.md":"# FastAPI Project\n\nGenerated from SRS requirements.\n"
    }

    for folder, files in structure.items():
        folder_path=os.path.join(base_dir,folder)
        os.makedirs(folder_path,exist_ok=True)
        for file in files:
            # path= os.path.join(folder_path,file)
            # name=file.split("/")[-1]
            content=file_contents.get(file,f"# {file}")
            with open(os.path.join(folder_path,file),"w",encoding="utf-8") as f:
                f.write(content)
    return base_dir

#for creating documentation

def collect_all_code(project_dir="generated_code"):
    code_list=[]
    for root,_,files in os.walk(project_dir):
        for file in files:
            if file.endswith(".py"):
                file_path=os.path.join(root,file)
                with open(file_path,"r",encoding="utf-8") as f:
                    code=f.read()
                    relative_path=os.path.relpath(file_path,project_dir)
                    code_list.append(f"# File: {relative_path}\n```python\n{code}\n")
    return "\n\n".join(code_list)


def generate_documentation():
    code_data=collect_all_code()
    api_doc_prompt=(
        "You are senior developer. Based on FastAPI project code,"
        "Generate the complete API documention file"
        f"{code_data}"
    )
    api_doc=call_groq_llama(api_doc_prompt)
    os.makedirs("generated_code",exist_ok=True)
    with open("generated_code/API_DOCUMENTATION.md","w",encoding="utf-8") as f:
        f.write(api_doc.strip())

    readme_prompt=(
        "Create the README.md file for the FastAPI project"
        "Give details about title, project description"
        f"{code_data}"
    )
    readme=call_groq_llama(readme_prompt)
    with open("generated_code/README.md","w",encoding="utf-8") as f:
        f.write(readme.strip())

    return "Documentation done"

# #working

# def generate_code_from_features(features_text: str) -> str:
#     GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#     headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
#     prompt = (f"Generate a FastAPI project with PostgreSQL based on these requirements:\n\n{features_text}\n\n"
#               "Please format your output with code as file path like:\n"
#               "# File: app/api/routes/user.py\n```python\n<code>\n```")

#     response = requests.post(
#         "https://api.groq.com/openai/v1/chat/completions",
#         headers=headers,
#         json={
#             "model": "llama3-70b-8192",
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0.3
#         }
#     )

#     if response.status_code != 200:
#         raise Exception(f"Groq error: {response.text}")

#     code_output = response.json()["choices"][0]["message"]["content"]

#     # Save code to a directory
#     project_dir = "generated_code"
#     if os.path.exists(project_dir):
#         import shutil
#         shutil.rmtree(project_dir)
#     os.makedirs(project_dir)

#     # Optional: parse and write the code into file structure
#     # For now, save everything to README.md inside project
#     # with open(os.path.join(project_dir, "README.md"), "w") as f:
#     #     f.write(code_output)

#     file_chunks=re.findall(
#         r"# File: (.+?)\n```(?:\w+)?\n(.*?)```",code_output,re.DOTALL
#     )
#     # if not file_chunks:
#     #     raise ValueError("No code")
#     for relative_path,code in file_chunks:
#         file_path=os.path.join(project_dir,relative_path.strip())
#         os.makedirs(os.path.dirname(file_path),exist_ok=True)
#         with open(file_path,  "w",encoding="utf-8") as f:
#             f.write(code.strip()+"\n")

#     zip_filename=f"{project_dir}.zip"
#     with ZipFile(zip_filename,"w") as zipf:
#         for foldername,subfolders,filenames in os.walk(project_dir):
#             for filename in filenames:
#                 file_path=os.path.join(foldername,filename)
#                 arcname=os.path.relpath(file_path,project_dir)
#                 zipf.write(file_path,arcname)

#     return zip_filename