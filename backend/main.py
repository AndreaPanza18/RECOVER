from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app import model_logic
import tempfile, shutil

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract")
async def extract_functional_requirements(
    file: UploadFile = File(...),
    provider: str = Form(...)
):
    # Salva file temporaneo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    results = model_logic.pipeline(temp_path, provider)
    return JSONResponse(content={"requirements": results})

@app.post("/userstory")
async def generate_user_stories(
    file: UploadFile = File(...),
    provider: str = Form(...)
):
    # Salva file temporaneo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    stories = model_logic.generate_userstories(temp_path, provider)
    return JSONResponse(content={"userstories": stories})