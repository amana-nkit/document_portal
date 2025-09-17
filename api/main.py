import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.document_ingestion.data_ingestion import (
    DocHandler,
    DocumentComparator,
    ChatIngestor,
)
from src.document_analyzer.data_analysis import DocumentAnalyzer
from src.document_compare.document_comparator import DocumentComparatorLLM
from src.document_chat.retrieval import ConversationalRAG
from utils.document_ops import FastAPIFileAdapter
from logger import GLOBAL_LOGGER as log

FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index") # where vector indexes are stored
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data") # where uploaded docs are stored.
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")  # <--- keep consistent with save_local()

app = FastAPI(title="Document Portal API", version="0.1") # Creates FastAPI app.

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates")) # Static files (/static) + Jinja2 templates (/templates) for UI.

app.add_middleware(   # Adds CORS middleware → allows frontend (Streamlit/React/anything) to call APIs.
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#=============== Endpoints =================
## Routes for UI homepage, health check, analyze, compare, chat index, chat query.

# ---------- UI Homepage ----------

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    log.info("Serving UI homepage.")
    resp = templates.TemplateResponse("index.html", {"request": request})
    resp.headers["Cache-Control"] = "no-store"
    return resp

# Serves index.html from templates.Cache disabled for fresh load each time.

# ---------- HEALTH CHECK ----------
@app.get("/health")
def health() -> Dict[str, str]:
    log.info("Health check passed.")
    return {"status": "ok", "service": "document-portal"}

# health endpoint for readiness/liveness probes

# # ---------- ANALYZE ----------
# @app.post("/analyze") # Upload a file → saves it → extracts text → runs DocumentAnalyzer (LLM-powered) → returns insights
# async def analyze_document(file: UploadFile = File(...)) -> Any:
#     try:
#         log.info(f"Received file for analysis: {file.filename}")
#         dh = DocHandler()
#         saved_path = dh.save_file(FastAPIFileAdapter(file))
#         text = dh.read_text(saved_path)   # <-- fixed (removed extra dh)
#         analyzer = DocumentAnalyzer()
#         result = analyzer.analyze_document(text)
#         log.info("Document analysis complete.")
#         return JSONResponse(content=result)
#     except HTTPException:
#         raise
#     except Exception as e:
#         log.exception("Error during document analysis")
#         raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    
# ---------- ANALYZE MULTIPLE DOCS (COMBINED) ----------
# ---------- ANALYZE MULTIPLE DOCS (LLM-powered) ----------
@app.post("/analyze")
async def analyze(
    files: List[UploadFile] = File(...),
    mode: str = Form("per-file")
):
    """
    Upload one or more files and analyze them with LLM.
    mode: 'per-file' → each file separately
          'combined' → merge all files and analyze once
    """
    try:
        dh = DocHandler()
        analyzer = DocumentAnalyzer()
        results = []

        if mode == "per-file":
            for f in files:
                # Save uploaded file to disk
                saved_path = dh.save_file(FastAPIFileAdapter(f))
                # Extract text
                text = dh.read_text(saved_path)
                # Run LLM analyzer
                result = analyzer.analyze_document(text)
                results.append({
                    "filename": f.filename,
                    "analysis": result
                })

        elif mode == "combined":
            combined_text = ""
            for f in files:
                saved_path = dh.save_file(FastAPIFileAdapter(f))
                combined_text += dh.read_text(saved_path) + "\n"

            result = analyzer.analyze_document(combined_text)
            results.append({
                "filenames": [f.filename for f in files],
                "analysis": result
            })

        else:
            raise HTTPException(status_code=400, detail="Invalid mode")

        return {"mode": mode, "results": results}

    except HTTPException:
        raise
    except Exception as e:
        log.exception("Error during document analysis")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

# @app.post("/analyze/combined")
# async def analyze_combined(files: List[UploadFile] = File(...)):
#     combined_text = ""
#     for f in files:
#         text = await f.read()
#         combined_text += text.decode("utf-8", errors="ignore") + "\n"
#     # Run combined analysis on all files
#     return {"mode": "combined", "length": len(combined_text)}

# ---------- CHAT: INDEX ----------
# Upload docs → creates ChatIngestor → chunks + embeds docs → stores in FAISS.
#Returns session info (so chat queries can reference the right FAISS index).

@app.post("/chat/index") 
async def chat_build_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),
) -> Any:
    try:
        log.info(f"Indexing chat session. Session ID: {session_id}, Files: {[f.filename for f in files]}")
        wrapped = [FastAPIFileAdapter(f) for f in files]
        # this is my main class for storing a data into VDB
        # created a object of ChatIngestor
        ci = ChatIngestor(
            temp_base=UPLOAD_BASE,
            faiss_base=FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None,
        )
        # NOTE: ensure your ChatIngestor saves with index_name="index" or FAISS_INDEX_NAME
        # e.g., if it calls FAISS.save_local(dir, index_name=FAISS_INDEX_NAME)
        ci.built_retriver(  # if your method name is actually build_retriever, fix it there as well
            wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k
        )
        log.info(f"Index created successfully for session: {ci.session_id}")
        return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Chat index building failed")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")

# ---------- CHAT: QUERY ----------
@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
) -> Any:
    try:
        log.info(f"Received chat query: '{question}' | session: {session_id}")
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs=True")

        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE  # type: ignore
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, detail=f"FAISS index not found at: {index_dir}")

        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir, k=k, index_name=FAISS_INDEX_NAME)  # build retriever + chain
        response = rag.invoke(question, chat_history=[])
        log.info("Chat query handled successfully.")

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG"
        }
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Chat query failed")
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

# command for executing the fast api
# uvicorn api.main:app --port 8080 --reload    
#uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload