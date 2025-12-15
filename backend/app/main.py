"""Main FastAPI application"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.api.routes import health, auth, transcribe, jobs, library, practice, snippets, export, analysis, ai, gospel, jazz, neosoul, blues, classical, curriculum, voicing, websocket  # audio
from app.services.transcription import TranscriptionService


# Global service instances
transcription_service: TranscriptionService = None
music_knowledge_base = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    global transcription_service, music_knowledge_base

    # Ensure directories exist
    settings.ensure_directories()

    # Initialize database
    from app.database.session import init_db
    await init_db()
    print("✓ Database initialized")

    # Initialize transcription service
    transcription_service = TranscriptionService()

    # Inject service into route modules
    transcribe.transcription_service = transcription_service
    jobs.transcription_service = transcription_service

    # Initialize music knowledge base
    from app.services.knowledge_base_loader import MusicKnowledgeBase
    music_knowledge_base = MusicKnowledgeBase()
    stats = music_knowledge_base.get_stats()
    if music_knowledge_base.is_loaded():
        print(f"✓ Music knowledge base loaded ({stats['style_guidelines_loaded']} genres)")
    else:
        print("⚠ Music knowledge base empty (run research script to populate)")

    print(f"✓ Started {settings.app_name} v{settings.version}")
    print(f"✓ Upload directory: {settings.UPLOAD_DIR}")
    print(f"✓ Output directory: {settings.OUTPUTS_DIR}")

    yield

    # Shutdown
    from app.database.session import close_db
    await close_db()
    print(f"✗ Shutting down {settings.app_name}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["auth"])
app.include_router(transcribe.router, prefix=settings.api_v1_prefix)
app.include_router(jobs.router, prefix=settings.api_v1_prefix)
app.include_router(library.router, prefix=settings.api_v1_prefix)
app.include_router(practice.router, prefix=settings.api_v1_prefix)
app.include_router(snippets.router, prefix=settings.api_v1_prefix)
app.include_router(export.router, prefix=settings.api_v1_prefix)
app.include_router(analysis.router, prefix=settings.api_v1_prefix)
app.include_router(ai.router, prefix=settings.api_v1_prefix)
app.include_router(curriculum.router, prefix=settings.api_v1_prefix)
# app.include_router(audio.router, prefix=settings.api_v1_prefix)  # Temporarily disabled - has bugs
app.include_router(gospel.router, prefix=settings.api_v1_prefix)
app.include_router(jazz.router, prefix=settings.api_v1_prefix)
app.include_router(neosoul.router, prefix=settings.api_v1_prefix)
app.include_router(blues.router, prefix=settings.api_v1_prefix)
app.include_router(classical.router, prefix=settings.api_v1_prefix)
app.include_router(voicing.router, prefix=settings.api_v1_prefix)
app.include_router(websocket.router, tags=["websocket"])  # WebSocket doesn't use prefix


# File serving endpoint
@app.get("/files/{job_id}/{filename}")
async def serve_file(job_id: str, filename: str):
    """Serve output files (MIDI, audio, etc.)"""
    file_path = settings.OUTPUTS_DIR / job_id / filename
    
    if not file_path.exists():
        return JSONResponse(
            status_code=404,
            content={"detail": "File not found"}
        )
    
    return FileResponse(file_path)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """API root"""
    return {
        "service": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "health": "/health",
    }
