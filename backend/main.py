from fastapi import FastAPI, UploadFile, File
from app.model_logic import pipeline
import shutil
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "RECOVER backend attivo!"}

@app.post("/extract")
async def extract_functional_requirements(file: UploadFile = File(...)):
    # Salva il file ricevuto temporaneamente
    temp_path = f"backend/temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        results = pipeline(temp_path)
    except Exception as e:
        return {"error": str(e)}
    finally:
        os.remove(temp_path)

    return {"functional_requirements": results}
