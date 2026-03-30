import os
import time
import google.generativeai as genai
from .schemas import BloodReportExtraction

def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)

def upload_to_gemini(path: str, mime_type: str = "application/pdf"):
    """Uploads the given file to Gemini File API."""
    print(f"Uploading '{path}' to Gemini...")
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the uploaded files to be processed by Gemini (required for PDFs/Videos)."""
    print("Waiting for file processing...")
    for file in files:
        current_file = genai.get_file(file.name)
        while current_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(5)
            current_file = genai.get_file(file.name)
        if current_file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process. State: {current_file.state.name}")
    print("\nFile processing complete.")

def extract_blood_report(pdf_path: str) -> BloodReportExtraction:
    configure_gemini()
    
    # 1. Upload the massive PDF document
    uploaded_file = upload_to_gemini(pdf_path)
    wait_for_files_active([uploaded_file])
    
    # 2. Setup the model. Using gemini-1.5-pro since accuracy is extremely important
    # for medical data over large contexts. Flash could also be used for higher speed.
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    
    # 3. Create the extraction prompt and run inference
    prompt = (
        "You are an expert medical data extractor. "
        "Review the attached blood/medical report carefully. Some pages may contain tables, "
        "scattered results, and doctor comments. Extract EVERY SINGLE test result, biomarker, "
        "and medical metric you can find. "
        "Ensure that for each item you identify the test name, value (quantity), measure (unit), "
        "normal/reference values or limits (normal valuelimit), and any comments associated "
        "with that specific metric (e.g. 'High', 'Low', 'Critical'). "
        "If there are overarching general comments from the doctor, place them in the general_comments field. "
        "CRITICAL: DO NOT extract boilerplate text, legal disclaimers, automated system warnings, or terms of service "
        "(e.g., 'This summary highlights...' or '...for informational purposes only'). "
        "Only extract actual medical conditions, diagnoses, or clinically relevant remarks written by a doctor."
    )
    
    try:
        print("Extracting data with Gemini... This may take up to a minute for long documents.")
        response = model.generate_content(
            [uploaded_file, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=BloodReportExtraction,
                temperature=0.0
            )
        )
        print("Extraction successful.")
        
        # Pydantic validation: parse the JSON response text back into the Pydantic schema
        # to ensure it is 100% compliant.
        parsed_data = BloodReportExtraction.model_validate_json(response.text)
        return parsed_data
        
    finally:
        # 4. Cleanup: Always delete from Google's servers after processing
        print("Cleaning up file from Gemini...")
        genai.delete_file(uploaded_file.name)
        print("Cleanup complete.")
