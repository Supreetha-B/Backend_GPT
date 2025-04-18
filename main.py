from fastapi import FastAPI
from routes import srs

app = FastAPI(title="SRS to FastAPI Generator")

@app.get("/")
def check():
    return {"message":"API is running"}
app.include_router(srs.router, prefix="/srs", tags=["SRS Utilities"])
