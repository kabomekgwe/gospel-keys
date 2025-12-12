"""AI Generator API Routes"""

from fastapi import APIRouter, HTTPException

from app.schemas.ai import (
    ProgressionRequest, ProgressionResponse,
    ReharmonizationRequest, ReharmonizationResponse,
    VoicingRequest, VoicingResponse,
    VoiceLeadingRequest, VoiceLeadingResponse,
    ExerciseRequest, ExerciseResponse,
    SubstitutionRequest, SubstitutionResponse,
    GeneratorsListResponse,
)
from app.services.ai_generator import ai_generator_service


router = APIRouter(prefix="/ai", tags=["AI Generator"])


@router.get("/generators", response_model=GeneratorsListResponse)
async def list_generators():
    """Get list of all available AI generators by category"""
    return ai_generator_service.get_available_generators()


@router.post("/progression", response_model=ProgressionResponse)
async def generate_progression(request: ProgressionRequest):
    """Generate a chord progression based on style, mood, and key"""
    try:
        return await ai_generator_service.generate_progression(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/reharmonization", response_model=ReharmonizationResponse)
async def generate_reharmonization(request: ReharmonizationRequest):
    """Get reharmonization suggestions for an existing progression"""
    try:
        return await ai_generator_service.generate_reharmonization(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reharmonization failed: {str(e)}")


@router.post("/voicing", response_model=VoicingResponse)
async def generate_voicings(request: VoicingRequest):
    """Generate multiple voicing options for a chord"""
    try:
        return await ai_generator_service.generate_voicings(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voicing generation failed: {str(e)}")


@router.post("/voice-leading", response_model=VoiceLeadingResponse)
async def optimize_voice_leading(request: VoiceLeadingRequest):
    """Find optimal voice leading between two chords"""
    try:
        return await ai_generator_service.optimize_voice_leading(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice leading failed: {str(e)}")


@router.post("/exercise", response_model=ExerciseResponse)
async def generate_exercise(request: ExerciseRequest):
    """Generate a practice exercise"""
    try:
        return await ai_generator_service.generate_exercise(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exercise generation failed: {str(e)}")


@router.post("/substitution", response_model=SubstitutionResponse)
async def get_substitutions(request: SubstitutionRequest):
    """Get chord substitution suggestions"""
    try:
        return await ai_generator_service.get_substitutions(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Substitution lookup failed: {str(e)}")
