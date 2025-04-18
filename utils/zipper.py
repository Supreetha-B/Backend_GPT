import zipfile
import os

# def zip_directory(source_dir:str,zip_path:str):
#     with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zipf:
#         for root,_,files in os.walk(source_dir):
#             for file in files:
#                 full_path=os.path.join(root,file)
#                 arcname=os.path.relpath(full_path,start=source_dir)
#                 zipf.write(full_path,arcname)

def zip_directory(project_path:str):
    zip_path=f"{project_path}.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zipf:
        for root,_,files in os.walk(project_path):
            for file in files:
                file_path=os.path.join(root,file)
                arcname=os.path.relpath(file_path,project_path)
                zipf.write(file_path,arcname)
    return zip_path