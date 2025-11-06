from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum

class MatchLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class JobDescription(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=50)
    required_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = Field(default=0, ge=0)

class MatchResult(BaseModel):
    match_score: float = Field(..., ge=0, le=100)
    match_level: MatchLevel
    matched_skills: List[str]
    missing_skills: List[str]
    key_highlights: List[str]
    recommendation: str

class BatchMatchRequest(BaseModel):
    job_description: JobDescription
    resume_count: int = Field(..., ge=1, le=50)

class BatchMatchResult(BaseModel):
    total_resumes: int
    rankings: List[Dict]
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    total_matches_processed: int
