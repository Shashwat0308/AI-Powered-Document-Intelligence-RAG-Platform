from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from sqlalchemy.orm import Session
import shutil

from backend.app.core.database import get_db
from backend.app.models.document import Document
from backend.app.models.user import User

from backend.app.services.rag_service import RAGService
from backend.app.api.auth import router as auth_router
from backend.app.api.dependencies import get_current_user


app = FastAPI(
    title="AI-Powered Document Intelligence & RAG Platform",
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# AUTHENTICATION ROUTES
# =========================

app.include_router(auth_router)


# =========================
# RAG SERVICE
# =========================

rag_service = RAGService()

rag_service.ingestion_service.load(
    "data/vector_store"
)


# =========================
# DOCUMENT DIRECTORY
# =========================

DOCUMENTS_DIR = Path("data/documents")

DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================
# REQUEST MODEL
# =========================

class ChatRequest(BaseModel):

    question: str

    top_k: int = 5


# =========================
# ROOT
# =========================

@app.get("/")
def root():

    return {
        "message": "AI Document Intelligence API is running"
    }


# =========================
# HEALTH
# =========================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================
# GET DOCUMENTS
# =========================

@app.get("/documents")
def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    documents = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id
        )
        .order_by(
            Document.uploaded_at.desc()
        )
        .all()
    )

    return {
        "documents": [
            {
                "id": document.id,
                "filename": document.filename,
                "file_size": document.file_size,
                "page_count": document.page_count,
                "chunk_count": document.chunk_count,
                "uploaded_at": document.uploaded_at
            }
            for document in documents
        ]
    }


# =========================
# UPLOAD DOCUMENT
# =========================

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # ---------------------------------
    # CHECK DUPLICATE DOCUMENT
    # ---------------------------------

    existing_document = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id,
            Document.filename == file.filename
        )
        .first()
    )

    if existing_document:

        return {
            "message": "Document already uploaded",
            "filename": file.filename,
            "pages": existing_document.page_count,
            "chunks": existing_document.chunk_count
        }

    # ---------------------------------
    # USER-SPECIFIC DOCUMENT DIRECTORY
    # ---------------------------------

    user_documents_dir = (
        DOCUMENTS_DIR / str(current_user.id)
    )

    user_documents_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        user_documents_dir / file.filename
    )

    try:

        # ---------------------------------
        # SAVE FILE
        # ---------------------------------

        with file_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        file_size = file_path.stat().st_size

        # ---------------------------------
        # PROCESS PDF
        # ---------------------------------

        result = (
            rag_service
            .ingestion_service
            .process_pdf(
                str(file_path),
                user_id=current_user.id
            )
        )

        # ---------------------------------
        # SAVE VECTOR STORE
        # ---------------------------------

        rag_service.ingestion_service.save(
            "data/vector_store"
        )

        # ---------------------------------
        # SAVE DOCUMENT IN DATABASE
        # ---------------------------------

        document = Document(

            user_id=current_user.id,

            filename=file.filename,

            file_path=str(file_path),

            file_size=file_size,

            page_count=result["pages"],

            chunk_count=result["chunks"]
        )

        db.add(document)

        db.commit()

        db.refresh(document)

        # ---------------------------------
        # RESPONSE
        # ---------------------------------

        return {

            "message":
                "Document uploaded and indexed successfully",

            "id":
                document.id,

            "filename":
                document.filename,

            "pages":
                document.page_count,

            "chunks":
                document.chunk_count
        }

    except Exception as e:

        # ---------------------------------
        # CLEANUP FILE IF PROCESSING FAILS
        # ---------------------------------

        if file_path.exists():

            file_path.unlink()

        raise HTTPException(

            status_code=500,

            detail=
                f"Document processing failed: {str(e)}"
        )


# =========================
# ASK QUESTION
# =========================

@app.post("/ask")
def ask(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):

    result = rag_service.ask(

        question=request.question,

        top_k=request.top_k,

        user_id=current_user.id
    )

    return result