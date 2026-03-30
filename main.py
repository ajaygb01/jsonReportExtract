import os
import uuid
import uvicorn
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.gemini_extractor import extract_blood_report
from src.schemas import BloodReportExtraction

load_dotenv()

app = FastAPI(
    title="Blood Report Extractor API",
    description="API for extracting structured JSON medical data from blood report PDFs.",
    version="1.0.0"
)

# Allow CORS so the frontend app can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_api_key(x_api_key: str = Header(None)):
    expected_api_key = os.getenv("APP_API_KEY")
    if not expected_api_key:
        raise HTTPException(status_code=500, detail="Server APP_API_KEY not configured in environment.")
    if x_api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key provided.")

@app.post("/extract", response_model=BloodReportExtraction, dependencies=[Depends(verify_api_key)])
async def extract_report(file: UploadFile = File(...)):
    """
    Accepts a PDF upload, extracts blood report data via Gemini, 
    and returns the structured JSON.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_filename = f"{uuid.uuid4()}_{file.filename}"
    local_tmp_path = os.path.join(os.getcwd(), "tmp", tmp_filename)
    os.makedirs(os.path.dirname(local_tmp_path), exist_ok=True)
    
    try:
        # 1. Save uploaded file to disk locally
        print(f"Receiving file {file.filename}...")
        with open(local_tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
        
    try:
        # 2. Extract with Gemini
        print(f"Extracting medical data via Gemini File API...")
        extraction_result = extract_blood_report(local_tmp_path)
        return extraction_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini extraction failed: {str(e)}")
    finally:
        # 3. Cleanup local downloaded file
        if os.path.exists(local_tmp_path):
            os.remove(local_tmp_path)
            print("Local tmp buffer deleted.")

if __name__ == "__main__":
    # Start the server locally
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
