from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import model_logic
import tempfile
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract")
async def extract_functional_requirements(file: UploadFile = File(...)):
    try:
        # Crea un file temporaneo nella directory di sistema
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        # Chiama la pipeline col path
        results = model_logic.pipeline(temp_path)

        return JSONResponse(content={"requirements": results})


    except Exception as e :

        import traceback

        traceback.print_exc()  # Stampa l'errore nel terminale

        return JSONResponse(content={"error" : str(e)}, status_code=500)



    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/userstory")
async def generate_user_stories(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        # Pipeline dedicata
        results = model_logic.generate_userstories(temp_path)

        return JSONResponse(content={"userstories": results})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)