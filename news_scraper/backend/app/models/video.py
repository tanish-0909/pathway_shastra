"""
Video Models - Pydantic models for video generation
"""
from pydantic import BaseModel
from typing import Optional


class VideoMetadata(BaseModel):
    """Metadata for a generated video"""
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    title: str = "Daily Market Briefing"
    subtitle: str = ""
    generated_at: Optional[str] = None
    status: str = "pending"  # pending, generating, completed, failed
    error: Optional[str] = None


class GenerateRequest(BaseModel):
    """Request to generate a new video"""
    force: bool = False  # Force regeneration even if already generated today


class VideoStatusResponse(BaseModel):
    """Response for video status check"""
    status: str
    generated_at: Optional[str] = None
    error: Optional[str] = None


class GenerateResponse(BaseModel):
    """Response after triggering video generation"""
    message: str
    status: str = "generating"
    metadata: Optional[VideoMetadata] = None
