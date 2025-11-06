from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import time
import os
from typing import Optional

from app.models import (
    JobDescription, MatchResult, HealthResponse,
    BatchMatchResult
)
from app.parser import parser
from app.matcher import matcher
from app.middleware import RateLimitMiddleware
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="AI-powered resume-to-job matching system with explainability"
)

# Add middleware
app.add_middleware(RateLimitMiddleware)

# Track stats
app.state.start_time = time.time()
app.state.total_matches = 0

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Resume-Job Matcher API",
        "version": settings.version,
        "endpoints": {
            "health": "/health",
            "match": "/match",
            "batch_match": "/batch-match",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health and stats"""
    uptime = time.time() - app.state.start_time
    
    return HealthResponse(
        status="healthy",
        version=settings.version,
        uptime_seconds=round(uptime, 2),
        total_matches_processed=app.state.total_matches
    )

@app.post("/match", response_model=MatchResult, tags=["Matching"])
async def match_resume(
    resume: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT)"),
    job_title: str = Form(..., description="Job title"),
    job_description: str = Form(..., description="Full job description"),
    required_skills: str = Form(default="", description="Comma-separated required skills")
):
    """
    Match a single resume against a job description
    
    Returns match score, matched/missing skills, and hiring recommendation
    """
    # Validate file extension
    file_extension = Path(resume.filename).suffix.lower()
    if file_extension not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions)}"
        )
    
    # Validate file size
    content = await resume.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_file_size / 1_000_000}MB"
        )
    
    # Save uploaded file temporarily
    file_path = UPLOAD_DIR / f"{int(time.time())}_{resume.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    try:
        # Parse resume
        resume_text = parser.parse_document(str(file_path))
        
        if len(resume_text) < 100:
            raise HTTPException(
                status_code=400,
                detail="Resume content too short. Minimum 100 characters required."
            )
        
        # Parse skills
        skills_list = [skill.strip() for skill in required_skills.split(",") if skill.strip()]
        
        # Perform matching
        result = matcher.match_resume_to_job(
            resume_text=resume_text,
            job_title=job_title,
            job_description=job_description,
            required_skills=skills_list
        )
        
        # Update stats
        app.state.total_matches += 1
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()

@app.post("/match-text", response_model=MatchResult, tags=["Matching"])
async def match_resume_text(
    resume_text: str = Form(..., min_length=100),
    job_title: str = Form(...),
    job_description: str = Form(..., min_length=50),
    required_skills: str = Form(default="")
):
    """
    Match resume text (no file upload) against a job description
    
    Useful for testing or when resume is already in text format
    """
    try:
        # Parse skills
        skills_list = [skill.strip() for skill in required_skills.split(",") if skill.strip()]
        
        # Perform matching
        result = matcher.match_resume_to_job(
            resume_text=resume_text,
            job_title=job_title,
            job_description=job_description,
            required_skills=skills_list
        )
        
        # Update stats
        app.state.total_matches += 1
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.exception_handler(413)
async def file_too_large_handler(request, exc):
    return JSONResponse(
        status_code=413,
        content={
            "detail": f"File too large. Maximum size: {settings.max_file_size / 1_000_000}MB"
        }
    )

@app.exception_handler(429)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={
            "detail": str(exc.detail),
            "rate_limit": settings.rate_limit_requests,
            "window_seconds": settings.rate_limit_window
        }
    )
