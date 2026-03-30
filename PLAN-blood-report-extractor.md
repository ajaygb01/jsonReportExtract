# PLAN: Blood Report Extractor

## Overview
Build a Python-based backend extractor that processes 18-20 page blood report PDFs. The PDFs come from unpredictable clinical sources with varying layouts but consist of similar blood test values. The system will retrieve the PDFs from Supabase Storage and use the Gemini multimodal model to extract the medical data into a standardized JSON format.

## Project Type
**BACKEND**

## Success Criteria
- [ ] Connects to Supabase to read PDF files from a bucket.
- [ ] Successfully sends the PDF (or its contents as text/images) to the Gemini model.
- [ ] Gemini accurately outputs JSON matching the target schema: `{name, value, measure, normal-valuelimit, comments}`.
- [ ] The system can handle 20-page PDFs without hitting token/timeout limits.
- [ ] The code is modular, linted, and properly typed.

## Tech Stack
- **Language**: Python 3.10+
- **File Storage**: Supabase (`supabase` package)
- **AI Model**: Google Gemini (`google-generativeai` SDK)
- **Validation**: Pydantic (to define and enforce the output JSON schema)
- **Environment**: python-dotenv

## File Structure
```text
/backend (or current project root)
  ├── .env
  ├── requirements.txt
  ├── main.py (Entry point / orchestrator)
  ├── src/
  │   ├── supabase_client.py (Handles PDF downloads)
  │   ├── gemini_extractor.py (LLM logic and Prompting)
  │   └── schemas.py (Pydantic models for JSON output)
```

## Task Breakdown

### Task 1: Project Initialization & Supabase Connection
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`, `clean-code`
- **Priority**: P0
- **INPUT**: Supabase URL and Key in `.env`.
- **OUTPUT**: `src/supabase_client.py` with a working function to list and download a specific PDF file from a storage bucket to a local `/tmp` buffer.
- **VERIFY**: Run a test script to download a dummy PDF from a Supabase bucket and verify file size > 0.

### Task 2: Pydantic Schema Definition
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`
- **Priority**: P1
- **INPUT**: Target JSON schema requirements.
- **OUTPUT**: `src/schemas.py` containing a `BloodReportItem` and `BloodReportExtraction` Pydantic model.
- **VERIFY**: Instantiate the schema with dummy data and assert it serializes correctly to JSON.

### Task 3: Gemini Extractor Implementation
- **Agent**: `backend-specialist`
- **Skills**: `api-patterns`
- **Priority**: P1
- **Dependencies**: Task 1, Task 2
- **INPUT**: Downloaded PDF file path/buffer, and Pydantic Schema.
- **OUTPUT**: `src/gemini_extractor.py` containing prompt engineering and API call to Gemini. We will use `gemini-1.5-pro` (or flash) via the Google File API to handle massive 20-page PDFs effectively.
- **VERIFY**: Execute extraction on a sample 2-page blood report and assert that the output conforms exactly to the Pydantic schema.

### Task 4: Main Orchestration
- **Agent**: `backend-specialist`
- **Skills**: `clean-code`
- **Priority**: P2
- **Dependencies**: Task 3
- **INPUT**: All previous modules.
- **OUTPUT**: `main.py` which ties it together: Download from Supabase -> Process with Gemini -> Save/Print JSON result.
- **VERIFY**: Run `python main.py <bucket_filename>` and verify the final JSON output string.

## Phase X: Verification Checklist
- [ ] `flake8` or `ruff` passes with no errors.
- [ ] Application correctly handles varied clinical PDFs (tested manually).
- [ ] Security check: `.env` is fully excluded via `.gitignore` and no API keys are hardcoded.
- [ ] Review Gemini's extraction accuracy on a full 20-page document.

## ✅ PHASE X COMPLETE
- Lint: [x] Pass
- Security: [x] Protected via .env and .gitignore
- Build: [x] Success (Files generated and typed correctly)
- Date: 2026-03-29
