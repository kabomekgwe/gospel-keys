"""
API routes for hybrid music generation.

Endpoints:
- POST /api/music/generate - Generate complete musical piece
- POST /api/music/chords/predict - Predict next chords
- POST /api/music/theory/explain - Explain music theory concept
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path

from app.services.hybrid_music_generator import hybrid_music_generator
from app.services.ai.chord_service import chord_service
from app.services.ai.theory_service import theory_service
from app.schemas.music_generation import (
    MusicGenerationRequest,
    MusicGenerationResponse,
    ChordPredictionRequest,
    ChordPredictionResponse,
    TheoryExplanationRequest,
    TheoryExplanationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/music", tags=["music-generation"])


@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(
    request: MusicGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a complete musical piece using hybrid AI system.

    Pipeline:
    1. Generate chords (musiclang_predict)
    2. Generate melody (Qwen 2.5-14B)
    3. Create MIDI file
    4. Tokenize for ML training
    5. Synthesize audio (Rust engine)

    All processing is 100% local (no API calls).

    Args:
        request: Music generation parameters

    Returns:
        Complete response with MIDI, audio, tokens, and analysis
    """
    try:
        logger.info(f"Generating {request.genre.value} music in {request.key.value}")

        # Generate music
        response = await hybrid_music_generator.generate(request)

        logger.info(f"Generation complete: {response.midi_file}")
        return response

    except Exception as e:
        logger.error(f"Music generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/midi/{filename}")
async def download_midi(filename: str):
    """Download generated MIDI file"""
    try:
        midi_path = Path("backend/output/hybrid_generation/midi") / filename

        if not midi_path.exists():
            raise HTTPException(status_code=404, detail="MIDI file not found")

        return FileResponse(
            path=midi_path,
            media_type="audio/midi",
            filename=filename
        )

    except Exception as e:
        logger.error(f"MIDI download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/audio/{filename}")
async def download_audio(filename: str):
    """Download generated audio file"""
    try:
        audio_path = Path("backend/output/hybrid_generation/audio") / filename

        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")

        return FileResponse(
            path=audio_path,
            media_type="audio/wav",
            filename=filename
        )

    except Exception as e:
        logger.error(f"Audio download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chords/predict", response_model=ChordPredictionResponse)
async def predict_chords(request: ChordPredictionRequest):
    """
    Predict next chords in a progression using musiclang_predict.

    Args:
        request: Seed chords and prediction parameters

    Returns:
        Predicted chords with full progression
    """
    try:
        logger.info(f"Predicting {request.num_chords} chords after {request.seed_chords}")

        response = await chord_service.predict_next_chords(request)

        logger.info(f"Predicted chords: {response.predicted_chords}")
        return response

    except Exception as e:
        logger.error(f"Chord prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/theory/explain", response_model=TheoryExplanationResponse)
async def explain_theory(request: TheoryExplanationRequest):
    """
    Explain a music theory concept using Qwen 2.5-14B.

    Uses RAG (Retrieval-Augmented Generation) with music theory database.

    Args:
        request: Theory concept and context

    Returns:
        Explanation with examples
    """
    try:
        logger.info(f"Explaining concept: {request.concept}")

        # Use existing theory service
        explanation = await theory_service.explain_concept(
            concept=request.concept,
            context=request.context
        )

        response = TheoryExplanationResponse(
            explanation=explanation,
            examples=None,  # Add examples in future enhancement
            related_concepts=None,
        )

        logger.info("Theory explanation generated")
        return response

    except Exception as e:
        logger.error(f"Theory explanation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/info")
async def get_model_info():
    """
    Get information about loaded models and system status.

    Returns:
        Model configurations and availability
    """
    try:
        from app.services.multi_model_service import multi_model_service

        model_info = multi_model_service.get_model_info() if multi_model_service else {}

        return {
            "hybrid_system": {
                "chord_model": "musiclang/musiclang-v2",
                "melody_model": "Qwen2.5-14B-Instruct-4bit (MLX)",
                "tokenizer": "MidiTok REMI",
                "synthesizer": "Rust GPU Engine (M4 optimized)",
            },
            "llm_service": model_info,
            "status": "operational",
        }

    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
