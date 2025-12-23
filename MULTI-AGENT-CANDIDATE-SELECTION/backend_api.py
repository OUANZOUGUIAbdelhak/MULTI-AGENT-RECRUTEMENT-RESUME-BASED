"""
FastAPI Backend for Multi-Agent Candidate Selection System
Connects React frontend to Python multi-agent backend
"""

import os
import sys
import uuid
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root.parent))

# Import backend components
from src.main import MultiAgentPipeline
from src.rag_new.rag_system import create_rag_system_from_config, RAGSystem
from src.config import RAW_DIR, DATA_DIR

# Jobs directory
JOBS_DIR = DATA_DIR / "jobs"
import pdfplumber

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Candidate Selection API",
    description="API for intelligent candidate evaluation using multi-agent AI system",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
rag_system: Optional[RAGSystem] = None
pipeline: Optional[MultiAgentPipeline] = None
evaluation_states: Dict[str, Dict[str, Any]] = {}
index_build_progress: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class JobOffer(BaseModel):
    title: str
    description: str
    requirements: str
    location: Optional[str] = None
    salary: Optional[str] = None

class EvaluationRequest(BaseModel):
    job_offer: JobOffer
    cv_ids: List[str]
    use_rag: bool = True
    max_candidates: int = 10

class AgentStatus(BaseModel):
    id: str
    name: str
    status: str  # waiting, processing, completed
    progress: int  # 0-100

class EvaluationStatus(BaseModel):
    evaluation_id: str
    status: str  # running, completed, error
    agents: List[AgentStatus]
    candidates: List[Dict[str, Any]]
    decision: Optional[Dict[str, Any]] = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system and pipeline on startup."""
    global rag_system, pipeline
    try:
        print("🚀 Initializing RAG system...")
        rag_system = create_rag_system_from_config()
        # Try to load existing index
        if rag_system.load_index():
            print("✅ RAG index loaded successfully")
        else:
            print("⚠️  No existing RAG index found. Build index using /api/build-index")
        
        pipeline = MultiAgentPipeline(rag_system)
        print("✅ Multi-agent pipeline initialized")
    except Exception as e:
        print(f"⚠️  Initialization warning: {e}")
        print("⚠️  System will work without RAG (using file system fallback)")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Multi-Agent Candidate Selection API",
        "status": "running",
        "rag_available": rag_system is not None and rag_system.index is not None
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "rag_system": rag_system is not None,
        "pipeline": pipeline is not None,
        "index_loaded": rag_system.index is not None if rag_system else False
    }


@app.post("/api/upload-cvs")
async def upload_cvs(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    """
    Upload CV files and optionally rebuild index with progress tracking.
    
    Returns list of uploaded file IDs and metadata, plus build_id if rebuilding index.
    """
    uploaded_files = []
    
    # Ensure DATA/raw directory exists
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        try:
            # Generate unique ID
            file_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix
            
            # Save file
            file_path = RAW_DIR / f"{file_id}{file_extension}"
            
            content = await file.read()
            file_path.write_bytes(content)
            
            uploaded_files.append({
                "id": file_id,
                "filename": file.filename,
                "size": len(content),
                "path": str(file_path),
                "upload_date": datetime.now().isoformat()
            })
            
            print(f"✅ Uploaded CV: {file.filename} -> {file_id}")
            
        except Exception as e:
            print(f"❌ Error uploading {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Error uploading {file.filename}: {str(e)}")
    
    # Rebuild RAG index if available (with progress tracking)
    build_id = None
    if rag_system and background_tasks:
        try:
            print("🔄 Rebuilding RAG index with new CVs...")
            build_id = str(uuid.uuid4())
            
            # Initialize progress
            index_build_progress[build_id] = {
                "status": "running",
                "step": "initializing",
                "progress": 0,
                "current_file": None,
                "total_files": 0,
                "processed_files": 0,
                "total_chunks": 0,
                "processed_chunks": 0,
                "message": "Starting index rebuild after CV upload...",
                "start_time": datetime.now().isoformat()
            }
            
            # Start rebuild in background
            background_tasks.add_task(build_index_with_progress, build_id)
            print(f"✅ Index rebuild started (build_id: {build_id})")
        except Exception as e:
            print(f"⚠️  Could not rebuild index: {e}")
    
    return {
        "success": True,
        "message": f"Uploaded {len(uploaded_files)} file(s)",
        "files": uploaded_files,
        "build_id": build_id  # Return build_id so frontend can track progress
    }


@app.post("/api/build-index")
async def build_index(background_tasks: BackgroundTasks):
    """Build or rebuild the RAG index with progress tracking."""
    global rag_system
    
    if not rag_system:
        try:
            rag_system = create_rag_system_from_config()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize RAG system: {str(e)}")
    
    # Generate build ID
    build_id = str(uuid.uuid4())
    
    # Initialize progress state
    index_build_progress[build_id] = {
        "status": "running",
        "step": "initializing",
        "progress": 0,
        "current_file": None,
        "total_files": 0,
        "processed_files": 0,
        "total_chunks": 0,
        "processed_chunks": 0,
        "message": "Starting index build...",
        "start_time": datetime.now().isoformat()
    }
    
    # Start building in background
    background_tasks.add_task(build_index_with_progress, build_id)
    
    return {
        "success": True,
        "build_id": build_id,
        "message": "Index build started"
    }


async def build_index_with_progress(build_id: str):
    """Build index with progress updates."""
    global rag_system, index_build_progress
    
    try:
        progress = index_build_progress[build_id]
        
        # Step 1: Load documents
        progress["step"] = "loading"
        progress["message"] = "Loading documents..."
        progress["progress"] = 5
        
        if not rag_system.data_dir.exists():
            raise ValueError(f"Data directory not found: {rag_system.data_dir}")
        
        from llama_index.core import SimpleDirectoryReader
        documents = SimpleDirectoryReader(
            input_dir=str(rag_system.data_dir),
            filename_as_id=True
        ).load_data()
        
        if not documents:
            raise ValueError(f"No documents found in {rag_system.data_dir}")
        
        progress["total_files"] = len(documents)
        progress["message"] = f"Loaded {len(documents)} document(s)"
        progress["progress"] = 15
        
        # Step 2: Configure metadata
        progress["step"] = "configuring"
        progress["message"] = "Configuring document metadata..."
        progress["progress"] = 20
        
        for doc in documents:
            doc.text_template = "Metadata:\n{metadata_str}\n---\nContent:\n{content}"
            if "page_label" not in doc.excluded_embed_metadata_keys:
                doc.excluded_embed_metadata_keys.append("page_label")
        
        progress["message"] = f"Configured {len(documents)} document(s)"
        progress["progress"] = 25
        
        # Step 3: Create text splitter
        progress["step"] = "splitting"
        progress["message"] = f"Splitting documents (chunk_size={rag_system.chunk_size})..."
        progress["progress"] = 30
        
        from llama_index.core.node_parser import SentenceSplitter
        text_splitter = SentenceSplitter(
            separator=" ",
            chunk_size=rag_system.chunk_size,
            chunk_overlap=rag_system.chunk_overlap
        )
        
        # Estimate chunks (rough estimate)
        total_text_length = sum(len(doc.text) for doc in documents)
        estimated_chunks = max(1, total_text_length // rag_system.chunk_size)
        progress["total_chunks"] = estimated_chunks
        progress["progress"] = 35
        
        # Step 4: Setup ChromaDB
        progress["step"] = "setup_chromadb"
        progress["message"] = "Setting up ChromaDB vector store..."
        progress["progress"] = 40
        
        chroma_collection = rag_system.chroma_client.get_or_create_collection(
            name=rag_system.collection_name
        )
        from llama_index.vector_stores.chroma import ChromaVectorStore
        from llama_index.core import StorageContext
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        progress["message"] = f"ChromaDB collection '{rag_system.collection_name}' ready"
        progress["progress"] = 45
        
        # Step 5: Create index with embeddings (this is the slow part)
        progress["step"] = "embedding"
        progress["message"] = "Creating embeddings and building vector index..."
        progress["progress"] = 50
        
        # Create a custom callback to track embedding progress
        class ProgressCallback:
            def __init__(self, progress_dict, total_docs):
                self.progress_dict = progress_dict
                self.total_docs = total_docs
                self.processed = 0
            
            def __call__(self, *args, **kwargs):
                self.processed += 1
                # Estimate progress: 50% start + 40% for embeddings
                embedding_progress = 50 + int((self.processed / self.total_docs) * 40)
                self.progress_dict["progress"] = min(90, embedding_progress)
                self.progress_dict["processed_files"] = self.processed
                self.progress_dict["message"] = f"Processing embeddings: {self.processed}/{self.total_docs} documents"
        
        from llama_index.core import VectorStoreIndex
        rag_system.index = VectorStoreIndex.from_documents(
            documents=documents,
            storage_context=storage_context,
            embed_model=rag_system.embed_model,
            transformations=[text_splitter],
            show_progress=True
        )
        
        progress["step"] = "finalizing"
        progress["message"] = "Finalizing index..."
        progress["progress"] = 90
        progress["processed_files"] = len(documents)
        
        # Step 6: Create query engine
        if rag_system.llm:
            progress["message"] = "Creating query engine..."
            progress["progress"] = 95
            
            from llama_index.core.prompts import PromptTemplate
            qa_prompt_template = PromptTemplate(
                "Context information is below.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Given the context information above and not prior knowledge, "
                "answer the following question in a clear, structured, and comprehensive manner.\n"
                "Provide a well-formatted answer based solely on the provided context.\n"
                "If the context does not contain enough information to answer the question, "
                "say so explicitly.\n\n"
                "Question: {query_str}\n"
                "Answer: "
            )
            try:
                rag_system.query_engine = rag_system.index.as_query_engine(
                    llm=rag_system.llm,
                    similarity_top_k=10,
                    response_mode="compact",
                    text_qa_template=qa_prompt_template
                )
            except TypeError:
                rag_system.query_engine = rag_system.index.as_query_engine(
                    llm=rag_system.llm,
                    similarity_top_k=10,
                    response_mode="compact"
                )
        
        progress["status"] = "completed"
        progress["step"] = "completed"
        progress["message"] = f"Index built successfully! Processed {len(documents)} documents."
        progress["progress"] = 100
        progress["end_time"] = datetime.now().isoformat()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        progress["status"] = "error"
        progress["message"] = f"Error: {str(e)}"
        progress["error"] = str(e)


@app.get("/api/index-build-progress/{build_id}")
async def get_index_build_progress(build_id: str):
    """Get index build progress."""
    if build_id not in index_build_progress:
        raise HTTPException(status_code=404, detail="Build not found")
    
    return index_build_progress[build_id]


@app.post("/api/start-evaluation")
async def start_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    """
    Start candidate evaluation process.
    
    Returns evaluation ID immediately, evaluation runs in background.
    """
    global pipeline
    
    if not pipeline:
        # Initialize pipeline if not already done
        if not rag_system:
            try:
                rag_system = create_rag_system_from_config()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to initialize RAG system: {str(e)}")
        pipeline = MultiAgentPipeline(rag_system)
    
    # Generate evaluation ID
    evaluation_id = str(uuid.uuid4())
    
    # Initialize evaluation state
    evaluation_states[evaluation_id] = {
        "status": "running",
        "agents": [
            {"id": "rh-agent", "name": "RH Agent", "status": "waiting", "progress": 0},
            {"id": "profile-agent", "name": "Profile Agent", "status": "waiting", "progress": 0},
            {"id": "technical-agent", "name": "Technical Agent", "status": "waiting", "progress": 0},
            {"id": "softskills-agent", "name": "Soft Skills Agent", "status": "waiting", "progress": 0},
            {"id": "decision-agent", "name": "Decision Agent", "status": "waiting", "progress": 0},
        ],
        "candidates": [],
        "decision": None,
        "job_offer": request.job_offer.dict(),
        "start_time": datetime.now().isoformat()
    }
    
    # Start evaluation in background
    background_tasks.add_task(
        run_evaluation,
        evaluation_id,
        request.job_offer,
        request.cv_ids,
        request.use_rag,
        request.max_candidates
    )
    
    return {
        "evaluation_id": evaluation_id,
        "status": "running",
        "message": "Evaluation started"
    }


async def run_evaluation(
    evaluation_id: str,
    job_offer: JobOffer,
    cv_ids: List[str],
    use_rag: bool,
    max_candidates: int
):
    """Run evaluation in background and update state."""
    global pipeline, evaluation_states
    
    try:
        state = evaluation_states[evaluation_id]
        
        # Step 1: RH Agent
        update_agent_status(evaluation_id, "rh-agent", "processing", 0)
        job_description = f"{job_offer.title}\n\n{job_offer.description}\n\nRequirements:\n{job_offer.requirements}"
        if job_offer.location:
            job_description += f"\nLocation: {job_offer.location}"
        if job_offer.salary:
            job_description += f"\nSalary: {job_offer.salary}"
        
        # Build criteria dict
        criteres = {}
        if job_offer.location:
            criteres["lieu"] = job_offer.location
        if job_offer.salary:
            criteres["salaire"] = job_offer.salary
        
        # Simulate progress for RH Agent
        for progress in [25, 50, 75, 100]:
            await asyncio.sleep(0.5)
            update_agent_status(evaluation_id, "rh-agent", "processing", progress)
        
        # Process job offer
        results = pipeline.process_job_offer(
            job_description=job_description,
            criteres=criteres if criteres else None,
            use_rag=use_rag and rag_system and rag_system.index is not None,
            max_candidates=max_candidates
        )
        
        update_agent_status(evaluation_id, "rh-agent", "completed", 100)
        
        # Step 2: Profile Agent (processes all candidates)
        update_agent_status(evaluation_id, "profile-agent", "processing", 0)
        candidates = results.get("candidates_evaluated", [])
        
        # Simulate progress
        for i, candidate in enumerate(candidates):
            progress = int((i + 1) / len(candidates) * 100) if candidates else 100
            update_agent_status(evaluation_id, "profile-agent", "processing", progress)
            await asyncio.sleep(0.3)
        
        update_agent_status(evaluation_id, "profile-agent", "completed", 100)
        
        # Step 3: Technical Agent
        update_agent_status(evaluation_id, "technical-agent", "processing", 0)
        for progress in [25, 50, 75, 100]:
            await asyncio.sleep(0.3)
            update_agent_status(evaluation_id, "technical-agent", "processing", progress)
        update_agent_status(evaluation_id, "technical-agent", "completed", 100)
        
        # Step 4: Soft Skills Agent
        update_agent_status(evaluation_id, "softskills-agent", "processing", 0)
        for progress in [25, 50, 75, 100]:
            await asyncio.sleep(0.3)
            update_agent_status(evaluation_id, "softskills-agent", "processing", progress)
        update_agent_status(evaluation_id, "softskills-agent", "completed", 100)
        
        # Step 5: Decision Agent
        update_agent_status(evaluation_id, "decision-agent", "processing", 0)
        for progress in [25, 50, 75, 100]:
            await asyncio.sleep(0.3)
            update_agent_status(evaluation_id, "decision-agent", "processing", progress)
        update_agent_status(evaluation_id, "decision-agent", "completed", 100)
        
        # Convert candidates to frontend format
        formatted_candidates = []
        for candidate in candidates:
            formatted_candidates.append({
                "id": candidate.get("candidate_id", str(uuid.uuid4())),
                "name": candidate.get("nom", "Unknown"),
                "scores": {
                    "profile": round(candidate.get("score_profil", 0), 1),
                    "technical": round(candidate.get("score_technique", 0), 1),
                    "softSkills": round(candidate.get("score_softskills", 0), 1),
                    "global": round(candidate.get("score_global", 0), 1)
                },
                "recommendation": map_recommendation(candidate.get("recommandation", "")),
                "justification": candidate.get("justification", ""),
                "aiJustification": candidate.get("justification", ""),
                "radarData": {
                    "profile": round(candidate.get("score_profil", 0), 1),
                    "technical": round(candidate.get("score_technique", 0), 1),
                    "softSkills": round(candidate.get("score_softskills", 0), 1),
                    "experience": 80,  # Default, can be extracted from profil_data
                    "education": 85,   # Default
                    "certifications": 75  # Default
                }
            })
        
        # Format decision output
        top_candidate = formatted_candidates[0] if formatted_candidates else None
        report = results.get("report", {})
        
        decision_output = None
        if top_candidate:
            decision_output = {
                "topCandidate": top_candidate,
                "confidence": 94,  # Can be calculated from scores
                "finalJustification": report.get("resume", ""),
                "totalCandidates": len(formatted_candidates)
            }
        
        # Update state
        state["status"] = "completed"
        state["candidates"] = formatted_candidates
        state["decision"] = decision_output
        state["end_time"] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        import traceback
        traceback.print_exc()
        state["status"] = "error"
        state["error"] = str(e)


def update_agent_status(evaluation_id: str, agent_id: str, status: str, progress: int):
    """Update agent status in evaluation state."""
    if evaluation_id in evaluation_states:
        agents = evaluation_states[evaluation_id]["agents"]
        for agent in agents:
            if agent["id"] == agent_id:
                agent["status"] = status
                agent["progress"] = progress
                break


def map_recommendation(rec: str) -> str:
    """Map backend recommendation to frontend format."""
    rec_lower = rec.lower()
    if "fortement" in rec_lower or "strongly" in rec_lower:
        return "strongly-recommended"
    elif "recommandé" in rec_lower or "recommended" in rec_lower:
        return "recommended"
    else:
        return "not-recommended"


@app.get("/api/evaluation/{evaluation_id}")
async def get_evaluation_status(evaluation_id: str):
    """Get evaluation status and results."""
    if evaluation_id not in evaluation_states:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    state = evaluation_states[evaluation_id]
    
    return {
        "status": state["status"],
        "agents": state["agents"],
        "candidates": state["candidates"],
        "decision": state["decision"],
        "error": state.get("error")
    }


@app.get("/api/files/resumes")
async def list_resume_files():
    """List all available resume files in DATA/raw."""
    files = []
    
    if RAW_DIR.exists():
        candidate_files = list(RAW_DIR.glob("*.txt")) + list(RAW_DIR.glob("*.pdf"))
        for file_path in candidate_files:
            try:
                files.append({
                    "id": file_path.stem,
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix.replace(".", ""),
                    "path": str(file_path.relative_to(DATA_DIR.parent))
                })
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
    
    return {"files": files}


@app.get("/api/files/job-offers")
async def list_job_offer_files():
    """List all available job offer files in DATA/jobs."""
    files = []
    
    if JOBS_DIR.exists():
        job_files = list(JOBS_DIR.glob("*.txt")) + list(JOBS_DIR.glob("*.pdf"))
        for file_path in job_files:
            try:
                files.append({
                    "id": file_path.stem,
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix.replace(".", ""),
                    "path": str(file_path.relative_to(DATA_DIR.parent))
                })
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
    
    return {"files": files}


@app.get("/api/files/job-offers/{file_id}")
async def get_job_offer_file(file_id: str):
    """Get content of a specific job offer file."""
    if not JOBS_DIR.exists():
        raise HTTPException(status_code=404, detail="Jobs directory not found")
    
    # Find file by ID (stem) or filename
    job_files = list(JOBS_DIR.glob("*.txt")) + list(JOBS_DIR.glob("*.pdf"))
    
    for file_path in job_files:
        if file_path.stem == file_id or file_path.name == file_id:
            try:
                if file_path.suffix.lower() == ".pdf":
                    import pdfplumber
                    text_parts = []
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text_parts.append(page_text)
                    content = "\n\n".join(text_parts)
                else:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                return {
                    "id": file_path.stem,
                    "filename": file_path.name,
                    "content": content,
                    "size": file_path.stat().st_size
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    raise HTTPException(status_code=404, detail="File not found")


class ProcessResumesRequest(BaseModel):
    file_ids: Optional[List[str]] = None

@app.post("/api/process-resumes")
async def process_selected_resumes(
    background_tasks: BackgroundTasks,
    request: ProcessResumesRequest
):
    """
    Process selected resume files and rebuild index with progress tracking.
    
    Args:
        request: Request body with file_ids list (stems) to process. If None, processes all files.
    """
    global rag_system
    
    if not rag_system:
        try:
            rag_system = create_rag_system_from_config()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize RAG system: {str(e)}")
    
    # Generate build ID
    build_id = str(uuid.uuid4())
    
    # Initialize progress state
    index_build_progress[build_id] = {
        "status": "running",
        "step": "initializing",
        "progress": 0,
        "current_file": None,
        "total_files": 0,
        "processed_files": 0,
        "total_chunks": 0,
        "processed_chunks": 0,
        "message": "Starting resume processing...",
        "start_time": datetime.now().isoformat(),
        "selected_files": request.file_ids or []
    }
    
    # Start processing in background
    background_tasks.add_task(process_resumes_with_progress, build_id, request.file_ids)
    
    return {
        "success": True,
        "build_id": build_id,
        "message": "Resume processing started"
    }


async def process_resumes_with_progress(build_id: str, file_ids: Optional[List[str]] = None):
    """Process selected resumes and rebuild index with progress updates."""
    global rag_system, index_build_progress
    
    try:
        progress = index_build_progress[build_id]
        
        # Count files to process
        if RAW_DIR.exists():
            all_files = list(RAW_DIR.glob("*.txt")) + list(RAW_DIR.glob("*.pdf"))
            if file_ids:
                files_to_process = [f for f in all_files if f.stem in file_ids]
            else:
                files_to_process = all_files
            
            progress["total_files"] = len(files_to_process)
            progress["message"] = f"Processing {len(files_to_process)} resume file(s)..."
            progress["progress"] = 10
            
            # Process each file
            for i, file_path in enumerate(files_to_process):
                progress["current_file"] = file_path.name
                progress["processed_files"] = i
                progress["progress"] = 10 + int((i / len(files_to_process)) * 20)
                progress["message"] = f"Processing {file_path.name} ({i+1}/{len(files_to_process)})..."
                await asyncio.sleep(0.1)  # Small delay for UI update
            
            progress["progress"] = 30
            progress["message"] = "Rebuilding index with processed resumes..."
        else:
            raise ValueError("DATA/raw directory not found")
        
        # Now rebuild index
        await build_index_with_progress(build_id)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        progress["status"] = "error"
        progress["message"] = f"Error: {str(e)}"
        progress["error"] = str(e)


if __name__ == "__main__":
    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

