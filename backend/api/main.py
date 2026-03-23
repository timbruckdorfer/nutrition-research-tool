"""
FastAPI Backend for Nutrition Research Paper Analyzer

This is the web API that provides endpoints for:
- File uploads (PDF papers)
- Paper analysis (via MCP server)
- Excel generation
- Results download

Architecture:
    Frontend → FastAPI (this file) → MCP Server → Tools (PDF, LLM)
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
import os
import uuid
import tempfile
from pathlib import Path
from datetime import datetime

# In-memory stores — nothing is written to the uploads folder
jobs = {}                  # job_id  -> status dict
pdf_store = {}             # file_id -> (original_filename, pdf_bytes)

# Create FastAPI app
app = FastAPI(
    title="Nutrition Research Paper Analyzer",
    description="AI-powered tool to extract structured data from research papers",
    version="1.0.0"
)

# Configure CORS (so frontend can talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only the results dir is needed (for Excel files while they're being downloaded)
BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Nutrition Research Paper Analyzer API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "results_dir": str(RESULTS_DIR),
        "results_dir_exists": RESULTS_DIR.exists(),
        "pdfs_in_memory": len(pdf_store),
        "active_jobs": len(jobs),
    }


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Accept PDF files and hold them in memory only — nothing written to disk.
    Returns file IDs for the subsequent /analyze call.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    uploaded_files = []

    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is not a PDF"
            )

        content = await file.read()
        file_id = str(uuid.uuid4())
        pdf_store[file_id] = (file.filename, content)

        uploaded_files.append({
            "file_id": file_id,
            "original_filename": file.filename,
            "size_bytes": len(content),
            "uploaded_at": datetime.now().isoformat()
        })

    return {
        "success": True,
        "files": uploaded_files,
        "total_files": len(uploaded_files)
    }


async def _run_analysis(job_id: str, file_ids: List[str]):
    """Background task: analyze papers and store result in jobs dict."""
    from .mcp_client import analyze_paper_via_mcp
    from .excel_generator import generate_excel

    total_papers = len(file_ids)
    results = []
    errors = []

    jobs[job_id]["total"] = total_papers

    for idx, file_id in enumerate(file_ids, 1):
        print(f"📄 Processing paper {idx}/{total_papers}...")
        jobs[job_id]["progress"] = idx

        if file_id not in pdf_store:
            print(f"   ❌ File not found in memory: {file_id}")
            errors.append({"file_id": file_id, "error": "File not found"})
            continue

        original_filename, pdf_bytes = pdf_store.pop(file_id)

        # Write to a temp file just for analysis, delete immediately after
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
        try:
            with os.fdopen(tmp_fd, "wb") as tmp:
                tmp.write(pdf_bytes)

            analysis_result = await analyze_paper_via_mcp(tmp_path)

            if analysis_result["success"]:
                results.append({
                    "english": analysis_result["data"],
                    "spanish": analysis_result.get("spanish_data", analysis_result["data"])
                })
                print(f"   ✅ Success: {analysis_result['data'].get('title', 'Unknown')[:60]}")
            else:
                error_msg = analysis_result.get("error", "Analysis failed")
                print(f"   ❌ Failed: {error_msg}")
                errors.append({"file_id": file_id, "error": error_msg})

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            errors.append({"file_id": file_id, "error": str(e)})
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    if results:
        print(f"\n📊 Generating Excel file with {len(results)} paper(s)...")
        excel_id = str(uuid.uuid4())
        excel_path = RESULTS_DIR / f"{excel_id}.xlsx"
        english_results = [r["english"] for r in results]
        spanish_results = [r["spanish"] for r in results]
        generate_excel(english_results, spanish_results, str(excel_path))
        print(f"✅ Excel file created: {excel_id}.xlsx")

        jobs[job_id].update({
            "status": "done",
            "excel_id": excel_id,
            "total_analyzed": len(results),
            "total_errors": len(errors),
            "errors": errors if errors else None,
        })
    else:
        jobs[job_id].update({
            "status": "failed",
            "error": f"No papers were successfully analyzed. Errors: {errors}",
        })


@app.post("/analyze")
async def analyze_papers(file_ids: List[str], background_tasks: BackgroundTasks):
    """
    Start analysis in the background and return a job_id immediately.
    Poll GET /status/{job_id} to track progress.
    """
    if not file_ids:
        raise HTTPException(status_code=400, detail="No file IDs provided")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "progress": 0, "total": len(file_ids)}

    background_tasks.add_task(_run_analysis, job_id, file_ids)

    return {"job_id": job_id, "status": "processing"}


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Poll this endpoint to check analysis progress.

    Returns:
        - status: "processing" | "done" | "failed"
        - progress / total: how many papers done so far
        - excel_id: set when status is "done"
        - error: set when status is "failed"
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/download/{excel_id}")
async def download_excel(excel_id: str):
    """
    Download the generated Excel file.
    """
    excel_path = RESULTS_DIR / f"{excel_id}.xlsx"
    
    if not excel_path.exists():
        raise HTTPException(status_code=404, detail="Excel file not found")
    
    return FileResponse(
        path=excel_path,
        filename=f"research_papers_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run when server starts."""
    print("=" * 60)
    print("🚀 Nutrition Research Paper Analyzer API Starting...")
    print("=" * 60)
    print(f"Results directory: {RESULTS_DIR}")
    print("PDFs: held in memory only (not written to disk)")
    print("\n✅ API Ready!")
    print("📖 Docs: http://localhost:8000/docs")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run when server stops."""
    print("\n👋 API shutting down...")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
