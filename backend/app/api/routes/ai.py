"""AI Generator API Routes"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, Query, Form
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import (
    ProgressionRequest, ProgressionResponse,
    ReharmonizationRequest, ReharmonizationResponse,
    VoicingRequest, VoicingResponse,
    VoiceLeadingRequest, VoiceLeadingResponse,
    ExerciseRequest, ExerciseResponse,
    SubstitutionRequest, SubstitutionResponse,
    LicksRequest, LicksResponse,
    GeneratorsListResponse,
    UsageStatsResponse, ModelUsageStats, TaskTypeStats,
    ArrangeRequest, ArrangeResponse,
    SplitVoicingRequest, SplitVoicingResponse,
    TheoryExplainRequest, TheoryExplainResponse,
    MidiTokenizeRequest, MidiTokenizeResponse,
    ChordPredictRequest, ChordPredictResponse,
    MidiGenerateRequest, MidiGenerateResponse
)
from app.schemas.music_generation import MusicGenerationRequest, MusicGenerationResponse, MusicGenre, MusicKey, VariationType
from enum import Enum
from app.services.ai_generator import ai_generator_service
from app.services.hybrid_music_generator import hybrid_music_generator
from app.services.template_loader import template_loader
from app.services.ai.theory_service import theory_service
from app.services.ai.midi_service import midi_service
from app.services.ai.chord_service import chord_service

from app.database.session import get_db
from app.database.models import ModelUsageLog


class TimeSignature(str, Enum):
    TS_4_4 = "4/4"
    TS_3_4 = "3/4"
    TS_6_8 = "6/8"
    TS_12_8 = "12/8"
    TS_2_4 = "2/4"
    TS_5_4 = "5/4"


class MusicStyle(str, Enum):
    TRADITIONAL = "traditional"
    MODERN = "modern"
    BEBOP = "bebop"
    BALLAD = "ballad"
    SWING = "swing"
    LATIN = "latin"
    FUSION = "fusion"
    GOSPEL_CHOPS = "gospel_chops"


router = APIRouter(prefix="/ai", tags=["AI Generator"])


@router.get("/generators", response_model=GeneratorsListResponse)
async def list_generators():
    """Get list of all available AI generators by category"""
    return ai_generator_service.get_available_generators()


@router.get("/templates", response_model=List[Dict[str, str]])
async def list_templates():
    """List available curriculum templates"""
    return template_loader.list_templates()


@router.post("/progression", response_model=ProgressionResponse)
async def generate_progression(
    request: ProgressionRequest,
    template_id: Optional[str] = Query(None, description="Optional ID of a curriculum template/exercise")
):
    """Generate a chord progression based on style, mood, and key"""
    try:
        return await ai_generator_service.generate_progression(request, template_id=template_id)
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
async def generate_exercise(
    request: ExerciseRequest,
    template_id: Optional[str] = Query(None, description="Optional ID of a curriculum template/exercise")
):
    """Generate a practice exercise"""
    try:
        return await ai_generator_service.generate_exercise(request, template_id=template_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exercise generation failed: {str(e)}")


@router.post("/substitution", response_model=SubstitutionResponse)
async def get_substitutions(request: SubstitutionRequest):
    """Get chord substitution suggestions"""
    try:
        return await ai_generator_service.get_substitutions(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Substitution lookup failed: {str(e)}")


@router.post("/licks", response_model=LicksResponse)
async def generate_licks(request: LicksRequest):
    """Generate jazz licks for chord or progression context"""
    try:
        return await ai_generator_service.generate_licks(request)
    except Exception as e:
        import traceback
        print(f"ERROR in generate_licks: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lick generation failed: {str(e)}")


@router.post("/arrange", response_model=ArrangeResponse)
async def arrange_progression(request: ArrangeRequest):
    """Convert chord progression to full two-hand MIDI arrangement

    Uses genre-specific arrangers to generate authentic piano arrangements:
    - Jazz: Rootless voicings, swing feel, bebop lines
    - Gospel: Polychords, runs, worship applications
    - Neo-Soul: Extended harmonies, laid-back timing
    - Blues: Shuffle feel, boogie bass, blues licks
    - Classical: Strict voice leading, period styles
    """
    try:
        return await ai_generator_service.arrange_progression(request)
    except Exception as e:
        import traceback
        print(f"ERROR in arrange_progression: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Arrangement failed: {str(e)}")


@router.post("/voicing/split", response_model=SplitVoicingResponse)
async def generate_split_voicing(request: SplitVoicingRequest):
    """Generate separate left and right hand voicings for a chord

    Returns optimized left/right hand split with proper voice leading.
    """
    try:
        # TODO: Implement split voicing generation
        # For now, return a simple implementation
        raise HTTPException(status_code=501, detail="Split voicing endpoint not yet implemented")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Split voicing failed: {str(e)}")


@router.get("/usage/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    days: int = 7,
    session: AsyncSession = Depends(get_db)
):
    """Get AI usage statistics for the last N days

    Args:
        days: Number of days to look back (default: 7)
        session: Database session

    Returns:
        UsageStatsResponse with aggregated statistics by model and task type
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Query all logs in the date range
        query = select(ModelUsageLog).where(
            ModelUsageLog.created_at >= start_date,
            ModelUsageLog.created_at <= end_date
        )
        result = await session.execute(query)
        logs = result.scalars().all()

        # Aggregate by model
        model_stats: Dict[str, Dict] = {}
        for log in logs:
            if log.model not in model_stats:
                model_stats[log.model] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'total_input_tokens': 0,
                    'total_output_tokens': 0,
                    'total_cost_usd': Decimal('0'),
                    'total_latency_ms': 0,
                }

            stats = model_stats[log.model]
            stats['total_requests'] += 1
            stats['successful_requests'] += 1 if log.success else 0
            stats['failed_requests'] += 0 if log.success else 1
            stats['total_input_tokens'] += log.input_tokens
            stats['total_output_tokens'] += log.output_tokens
            stats['total_cost_usd'] += log.cost_usd
            stats['total_latency_ms'] += log.latency_ms

        # Aggregate by task type
        task_stats: Dict[str, Dict] = {}
        for log in logs:
            if log.task_type not in task_stats:
                task_stats[log.task_type] = {
                    'total_requests': 0,
                    'total_cost_usd': Decimal('0'),
                }

            task_stats[log.task_type]['total_requests'] += 1
            task_stats[log.task_type]['total_cost_usd'] += log.cost_usd

        # Build response models
        models_list = [
            ModelUsageStats(
                model=model,
                total_requests=stats['total_requests'],
                successful_requests=stats['successful_requests'],
                failed_requests=stats['failed_requests'],
                total_input_tokens=stats['total_input_tokens'],
                total_output_tokens=stats['total_output_tokens'],
                total_cost_usd=float(stats['total_cost_usd']),
                avg_latency_ms=stats['total_latency_ms'] / stats['total_requests'] if stats['total_requests'] > 0 else 0.0
            )
            for model, stats in model_stats.items()
        ]

        task_types_list = [
            TaskTypeStats(
                task_type=task_type,
                total_requests=stats['total_requests'],
                total_cost_usd=float(stats['total_cost_usd'])
            )
            for task_type, stats in task_stats.items()
        ]

        # Calculate totals
        total_requests = sum(stats['total_requests'] for stats in model_stats.values())
        total_cost_usd = float(sum(stats['total_cost_usd'] for stats in model_stats.values()))

        return UsageStatsResponse(
            period_days=days,
            total_requests=total_requests,
            total_cost_usd=total_cost_usd,
            models=models_list,
            task_types=task_types_list,
            date_range={
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")


# === Phase 1 & 2: Local AI Stack Routes ===

@router.post("/theory/explain", response_model=TheoryExplainResponse)
async def explain_theory(request: TheoryExplainRequest):
    """Explain a music theory concept using local LLM (Qwen)"""
    try:
        explanation = await theory_service.explain_concept(request.concept, request.context)
        return TheoryExplainResponse(explanation=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Theory explanation failed: {str(e)}")

@router.post("/chords/predict", response_model=ChordPredictResponse)
async def predict_chords(request: ChordPredictRequest):
    """Predict next chords using MusicLang"""
    try:
        predictions = await chord_service.predict_next_chords(request.progression, request.num_chords)
        return ChordPredictResponse(predicted_chords=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chord prediction failed: {str(e)}")

@router.post("/midi/tokenize", response_model=MidiTokenizeResponse)
async def tokenize_midi(request: MidiTokenizeRequest):
    """Tokenize a MIDI file using MidiTok"""
    try:
        tokens = midi_service.tokenize_midi_file(request.file_path)
        return MidiTokenizeResponse(tokens=tokens)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="MIDI file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tokenization failed: {str(e)}")

@router.post("/midi/generate", response_model=MidiGenerateResponse)
async def generate_midi(request: MidiGenerateRequest):
    """Generate MIDI from text prompt using MusicLang"""
    try:
        midi_path = await chord_service.generate_score(
            prompt=request.prompt,
            num_tokens=request.num_tokens
        )
        if midi_path:
            return MidiGenerateResponse(
                success=True,
                midi_file_path=midi_path,
                message="MIDI generated successfully"
            )
        else:
            return MidiGenerateResponse(
                success=False,
                message="Failed to generate MIDI"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MIDI generation failed: {str(e)}")


@router.post(
    "/generate/hybrid",
    response_model=MusicGenerationResponse,
    summary="Generate Hybrid Music (World Class Mode)",
    description="""
    **Generate professional-quality music using the Hybrid Generator engine.**
    
    This endpoint combines template-based generation with AI orchestration to produce high-quality MIDI and Audio.
    Uses **Form Data** for easy Swagger testing.
    
    **Key Features:**
    *   **World Class Jazz**: Uses sophisticated shell voicings and realistic hand-splitting for piano.
    *   **Templates**: deterministic structure using industry-standard templates (via `template_data`).
    *   **Humanization**: automatically injects micro-timing and velocity humanization.
    
    **Parameters:**
    *   `genre`: Target musical style (e.g., 'jazz', 'gospel').
    *   `complexity` (1-10): Higher values = richer harmony, more extensions, denser arrangement.
    *   `num_bars`: Length of the piece (templates will loop to fill this).
    *   `include_melody` / `include_chords`: Toggle tracks for "mixed" or isolated output.
    *   `prompt`: Optional text description for metadata.
    """,
    responses={
        200: {
            "description": "Successful generation",
            "content": {
                "application/json": {
                    "example": {
                        "midi_file": "backend/output/hybrid/jazz_C_12345.mid",
                        "generation_time_ms": 2500,
                        "model_info": {"synthesizer": "Rust GPU Engine"}
                    }
                }
            }
        },
        500: {"description": "Generation failed (internal error)"}
    }
)
async def generate_hybrid_music(
    genre: MusicGenre = Form(..., description="Musical genre"),
    key: MusicKey = Form(MusicKey.C, description="Key signature"),
    tempo: int = Form(120, description="Tempo in BPM"),
    num_bars: int = Form(8, description="Number of bars to generate"),
    time_signature: TimeSignature = Form(TimeSignature.TS_4_4, description="Time signature"),
    style: MusicStyle = Form(MusicStyle.TRADITIONAL, description="Style variation"),
    complexity: int = Form(5, description="Complexity level 1-10"),
    variations: Optional[List[VariationType]] = Form(None, description="Variations to apply to repeated bars"),
    include_melody: bool = Form(True, description="Generate melody"),
    include_bass: bool = Form(True, description="Generate bass line"),
    include_chords: bool = Form(True, description="Include chord voicings"),
    synthesize_audio: bool = Form(True, description="Generate audio file"),
    use_gpu_synthesis: bool = Form(True, description="Use GPU-accelerated synthesis"),
    add_reverb: bool = Form(True, description="Add reverb effect"),
    prompt: Optional[str] = Form(None, description="Optional prompt override")
):
    """
    Generate music using the Hybrid Generator (Form Data).
    """
    try:
        import json
        
        # reconstruct request object
        request_data = MusicGenerationRequest(
            genre=genre, 
            key=key,
            tempo=tempo,
            num_bars=num_bars,
            time_signature=time_signature.value,
            style=style.value,
            complexity=complexity,
            variations=variations,
            include_melody=include_melody,
            include_bass=include_bass,
            include_chords=include_chords,
            synthesize_audio=synthesize_audio,
            use_gpu_synthesis=use_gpu_synthesis,
            add_reverb=add_reverb,
            template_data=None # defaults for form
        )
        
        # Map "Mixed" concept if needed (already handled by bool flags)
        
        response = await hybrid_music_generator.generate(request_data)
        return response
    except Exception as e:
        import traceback
        print(f"ERROR in generate_hybrid_music: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Hybrid generation failed: {str(e)}")


