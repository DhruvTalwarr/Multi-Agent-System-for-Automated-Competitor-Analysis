import io
from typing import Optional
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pypdf

# Import compiled LangGraph instance from graph.py
from graph import app as agent_app  

app = FastAPI(title="Smart Business Decision Assistant (SBDA)")

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_file_text(file_bytes: bytes, filename: str) -> str:
    """Extract readable text from plain text or PDF files."""
    if filename.lower().endswith(".pdf"):
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text_pages = [
                page.extract_text() for page in pdf_reader.pages if page.extract_text()
            ]
            return "\n".join(text_pages)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF file: {str(e)}")
    else:
        # Fallback for plain text files (.txt, .csv, .md, .json)
        return file_bytes.decode("utf-8", errors="ignore")

@app.post("/api/chat")
async def analyze(
    prompt: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    try:
        file_content = ""
        
        # Read and parse uploaded file if provided
        if file:
            content_bytes = await file.read()
            file_content = extract_file_text(content_bytes, file.filename)
            
            # Truncate content slightly if text is exceptionally long to avoid TPM limits
            max_chars = 12000
            if len(file_content) > max_chars:
                file_content = file_content[:max_chars] + "\n...[Content Truncated]"
                
            print(f"Received file: {file.filename} (Extracted {len(file_content)} characters)")

        # Combine text prompt and parsed file content
        combined_query = prompt
        if file_content.strip():
            combined_query += f"\n\n[Attached File Content - {file.filename}]:\n{file_content}"

        # Initialize input state for LangGraph
        initial_input = {
            "messages": [combined_query],
            "revision_count": 0,
            "is_approved": False
        }
        
        # Invoke LangGraph app
        result = agent_app.invoke(initial_input)
        report_text = result.get("report", "No report generated.")
        
        return {
            "status": "success",
            "reply": report_text,
            "iterations": result.get("revision_count", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)