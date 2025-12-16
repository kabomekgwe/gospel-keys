"""
Theory Lab API Endpoints

Interactive theory exploration with real-time audio preview.
Uses existing theory library + AI orchestrator for explanations.

Complexity Routing:
- Simple operations (4): Phi-3.5 Mini
- Explanations (5-6): Qwen2.5-7B
- Complex analysis (7-8): Gemini Pro
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_orchestrator import ai_orchestrator, TaskType
from app.theory.voice_leading_neo_riemannian import (
    apply_parallel_transform,
    apply_leading_tone_transform,
    apply_relative_transform,
    get_plr_transformation_sequence,
    generate_tonnetz_neighbors,
    get_tonnetz_path,
    calculate_tonnetz_distance,
    get_hexatonic_pole,
    apply_neo_riemannian_to_progression,
)
from app.theory.chord_substitutions import (
    get_negative_harmony_chord,
    get_negative_harmony_progression,
    apply_coltrane_changes,
    get_giant_steps_cycle,
    get_sixth_diminished_scale,
    get_all_substitution_options,
    suggest_reharmonization,
)
from app.theory.chord_library import get_chord_notes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/theory-tools", tags=["theory-tools"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class ChordInput(BaseModel):
    """Single chord input"""
    root: str = Field(..., description="Chord root (e.g., 'C', 'F#')")
    quality: str = Field("", description="Chord quality (e.g., '', 'm', '7', 'maj7')")


class PLRTransformRequest(BaseModel):
    """Request for PLR transformation"""
    chord_root: str = Field(..., description="Chord root")
    chord_quality: str = Field("", description="Chord quality")
    transformation: str = Field(..., description="Transformation type: 'P', 'L', or 'R'")
    octave: int = Field(4, description="Starting octave")
    prefer_sharps: bool = Field(True, description="Use sharps instead of flats")
    student_level: str = Field("intermediate", description="Student level for AI explanation")


class PLRPathRequest(BaseModel):
    """Request for shortest PLR path between chords"""
    start_chord: ChordInput
    end_chord: ChordInput
    max_steps: int = Field(6, description="Maximum path length")
    student_level: str = Field("intermediate", description="Student level for explanation")


class TonnetzNeighborsRequest(BaseModel):
    """Request for Tonnetz neighbors"""
    chord_root: str
    chord_quality: str = ""
    octave: int = 4
    prefer_sharps: bool = True


class NegativeHarmonyRequest(BaseModel):
    """Request for negative harmony transformation"""
    progression: List[Tuple[str, str]] = Field(..., description="List of (root, quality) tuples")
    key_root: str = Field(..., description="Key root")
    key_quality: str = Field("major", description="major or minor")
    octave: int = 4
    prefer_sharps: bool = True
    student_level: str = Field("intermediate", description="Student level")


class ColtraneChangesRequest(BaseModel):
    """Request for Coltrane Changes generation"""
    target_key: str = Field(..., description="Target key")
    octave: int = 4
    prefer_sharps: bool = True
    student_level: str = Field("advanced", description="Student level")


class SubstitutionAnalysisRequest(BaseModel):
    """Request for substitution analysis"""
    chord_root: str
    quality: str = ""
    key_root: str
    key_quality: str = "major"
    complexity_level: str = Field("moderate", description="simple, moderate, or complex")
    octave: int = 4
    prefer_sharps: bool = True


class BarryHarrisRequest(BaseModel):
    """Request for Barry Harris 6th-diminished scale"""
    root: str
    octave: int = 4
    prefer_sharps: bool = True
    student_level: str = Field("advanced", description="Student level")


class TransformationResponse(BaseModel):
    """Response for transformation"""
    new_root: str
    new_quality: str
    voicing: List[str]
    metadata: Dict[str, Any]
    ai_explanation: Optional[str] = None


# ============================================================================
# NEO-RIEMANNIAN TRANSFORMATIONS
# ============================================================================


@router.post("/neo-riemannian/transform", response_model=TransformationResponse)
async def neo_riemannian_transform(request: PLRTransformRequest):
    """
    Apply a single PLR transformation to a chord.

    Returns transformed chord with AI-generated explanation.
    """
    try:
        # Apply transformation
        if request.transformation.upper() == 'P':
            result = apply_parallel_transform(
                request.chord_root,
                request.chord_quality,
                request.octave,
                request.prefer_sharps
            )
        elif request.transformation.upper() == 'L':
            result = apply_leading_tone_transform(
                request.chord_root,
                request.chord_quality,
                request.octave,
                request.prefer_sharps
            )
        elif request.transformation.upper() == 'R':
            result = apply_relative_transform(
                request.chord_root,
                request.chord_quality,
                request.octave,
                request.prefer_sharps
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transformation: {request.transformation}. Use 'P', 'L', or 'R'"
            )

        new_root, new_quality, voicing, metadata = result

        # Generate AI explanation (Complexity 5-6: Qwen2.5-7B)
        explanation_prompt = f"""Explain the {request.transformation} transformation from {request.chord_root}{request.chord_quality} to {new_root}{new_quality} for a {request.student_level} student.

Transformation: {metadata.get('description')}
Voice moved: {metadata.get('voice_moved')}
Semitones moved: {metadata.get('semitones_moved')}

Provide a brief (2-3 sentences) explanation that:
1. Describes which note changed
2. Explains why this creates smooth voice leading
3. Gives a musical context where this is commonly used

Keep it conversational and student-friendly."""

        try:
            # Use ai_orchestrator for explanation (will route to Qwen2.5-7B)
            ai_response = await ai_orchestrator.generate_with_fallback(
                prompt=explanation_prompt,
                task_type=TaskType.THEORY_ANALYSIS,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 512,
                    "response_mime_type": "text/plain",
                },
                cache_ttl_hours=24
            )
            explanation = ai_response if isinstance(ai_response, str) else ai_response.get("text", "")
        except Exception as e:
            logger.warning(f"AI explanation failed: {e}")
            explanation = f"The {request.transformation} transformation changes {metadata.get('voice_moved')} by {metadata.get('semitones_moved')} semitones."

        return TransformationResponse(
            new_root=new_root,
            new_quality=new_quality,
            voicing=voicing,
            metadata=metadata,
            ai_explanation=explanation
        )

    except Exception as e:
        logger.error(f"Neo-Riemannian transformation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/neo-riemannian/path")
async def neo_riemannian_path(request: PLRPathRequest):
    """
    Find shortest PLR path between two chords.

    Returns transformation sequence with voice leading analysis.
    """
    try:
        # Find path
        path = get_tonnetz_path(
            request.start_chord.root,
            request.start_chord.quality,
            request.end_chord.root,
            request.end_chord.quality,
            request.max_steps
        )

        if path is None:
            return {
                "path_found": False,
                "message": f"No path found within {request.max_steps} steps",
                "start_chord": f"{request.start_chord.root}{request.start_chord.quality}",
                "end_chord": f"{request.end_chord.root}{request.end_chord.quality}"
            }

        # Calculate distance
        distance = calculate_tonnetz_distance(
            request.start_chord.root,
            request.start_chord.quality,
            request.end_chord.root,
            request.end_chord.quality
        )

        # Generate sequence details
        sequence = get_plr_transformation_sequence(
            request.start_chord.root,
            request.start_chord.quality,
            "".join(path),
            octave=4,
            prefer_sharps=True
        )

        # Generate AI explanation
        explanation_prompt = f"""Explain the PLR path from {request.start_chord.root}{request.start_chord.quality} to {request.end_chord.root}{request.end_chord.quality} for a {request.student_level} student.

Path: {' → '.join(path)}
Distance: {distance} transformations

Explain:
1. What this path represents harmonically
2. Why this is the most efficient voice leading route
3. Musical context where this progression might be used

Keep it brief (2-3 sentences)."""

        try:
            ai_response = await ai_orchestrator.generate_with_fallback(
                prompt=explanation_prompt,
                task_type=TaskType.THEORY_ANALYSIS,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 512,
                    "response_mime_type": "text/plain",
                }
            )
            explanation = ai_response if isinstance(ai_response, str) else ai_response.get("text", "")
        except Exception:
            explanation = f"This path uses {len(path)} transformations: {' → '.join(path)}"

        return {
            "path_found": True,
            "path": path,
            "distance": distance,
            "sequence": [
                {
                    "root": item[0],
                    "quality": item[1],
                    "voicing": item[2],
                    "metadata": item[3]
                }
                for item in sequence
            ],
            "ai_explanation": explanation
        }

    except Exception as e:
        logger.error(f"PLR path calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tonnetz/neighbors")
async def tonnetz_neighbors(request: TonnetzNeighborsRequest):
    """
    Get all Tonnetz neighbors (one PLR transformation away).

    Returns P, L, and R neighbors with distances.
    """
    try:
        neighbors = generate_tonnetz_neighbors(
            request.chord_root,
            request.chord_quality,
            request.octave,
            request.prefer_sharps
        )

        return {
            "original_chord": f"{request.chord_root}{request.chord_quality}",
            "neighbors": {
                name: {
                    "root": chord[0],
                    "quality": chord[1],
                    "voicing": chord[2]
                }
                for name, chord in neighbors.items()
            }
        }

    except Exception as e:
        logger.error(f"Tonnetz neighbors calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NEGATIVE HARMONY
# ============================================================================


@router.post("/negative-harmony/generate")
async def negative_harmony_generate(request: NegativeHarmonyRequest):
    """
    Generate negative harmony version of a progression.

    Returns negative progression with comparison and AI explanation.
    """
    try:
        # Generate negative harmony
        negative_prog = get_negative_harmony_progression(
            request.progression,
            request.key_root,
            request.key_quality,
            request.octave,
            request.prefer_sharps
        )

        # Generate AI explanation (Complexity 6-7: Qwen2.5-7B)
        original_str = " → ".join([f"{r}{q}" for r, q in request.progression])
        negative_str = " → ".join([chord[0] for chord in negative_prog])

        explanation_prompt = f"""Explain negative harmony transformation for a {request.student_level} student.

Key: {request.key_root} {request.key_quality}
Original: {original_str}
Negative: {negative_str}

Explain:
1. What negative harmony is (axis of reflection concept)
2. Why these specific chords are the negative harmony equivalents
3. How this creates a similar but fresh harmonic feeling

Keep it educational and concise (3-4 sentences)."""

        try:
            ai_response = await ai_orchestrator.generate_with_fallback(
                prompt=explanation_prompt,
                task_type=TaskType.THEORY_ANALYSIS,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                    "response_mime_type": "text/plain",
                }
            )
            explanation = ai_response if isinstance(ai_response, str) else ai_response.get("text", "")
        except Exception:
            explanation = "Negative harmony creates mirror-image chord relationships around a central axis."

        return {
            "original_progression": [
                {"root": r, "quality": q}
                for r, q in request.progression
            ],
            "negative_progression": [
                {
                    "symbol": chord[0],
                    "voicing": chord[1]
                }
                for chord in negative_prog
            ],
            "key": f"{request.key_root} {request.key_quality}",
            "ai_explanation": explanation
        }

    except Exception as e:
        logger.error(f"Negative harmony generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COLTRANE CHANGES
# ============================================================================


@router.post("/coltrane/generate")
async def coltrane_generate(request: ColtraneChangesRequest):
    """
    Generate Coltrane Changes (Giant Steps pattern).

    Returns progression with AI explanation of harmonic movement.
    """
    try:
        # Generate Coltrane changes
        progression = apply_coltrane_changes(
            request.target_key,
            request.octave,
            request.prefer_sharps
        )

        # Generate AI explanation (Complexity 7-8: Qwen2.5-7B or Gemini)
        prog_str = " → ".join([chord[0] for chord in progression])

        explanation_prompt = f"""Explain Coltrane Changes to an {request.student_level} student.

Target key: {request.target_key}
Progression: {prog_str}

Explain:
1. What Coltrane Changes are (Giant Steps pattern)
2. How the progression moves through three tonal centers (major thirds apart)
3. Why this creates harmonic complexity
4. How to practice navigating this progression

Be detailed but clear (4-5 sentences)."""

        try:
            ai_response = await ai_orchestrator.generate_with_fallback(
                prompt=explanation_prompt,
                task_type=TaskType.THEORY_ANALYSIS,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                    "response_mime_type": "text/plain",
                }
            )
            explanation = ai_response if isinstance(ai_response, str) else ai_response.get("text", "")
        except Exception:
            explanation = "Coltrane Changes move through three tonal centers separated by major thirds."

        return {
            "target_key": request.target_key,
            "progression": [
                {
                    "symbol": chord[0],
                    "voicing": chord[1]
                }
                for chord in progression
            ],
            "ai_explanation": explanation
        }

    except Exception as e:
        logger.error(f"Coltrane Changes generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUBSTITUTIONS
# ============================================================================


@router.post("/substitutions/analyze")
async def analyze_substitutions(request: SubstitutionAnalysisRequest):
    """
    Analyze all possible substitution options for a chord.

    Returns categorized substitutions with explanations.
    """
    try:
        # Get all substitution options
        options = get_all_substitution_options(
            request.chord_root,
            request.quality,
            request.key_root,
            request.key_quality,
            request.octave,
            request.prefer_sharps
        )

        # Format response
        formatted_options = {}
        for category, subs in options.items():
            formatted_options[category] = [
                {
                    "symbol": sub[0],
                    "voicing": sub[1]
                }
                for sub in subs
            ]

        return {
            "original_chord": f"{request.chord_root}{request.quality}",
            "key": f"{request.key_root} {request.key_quality}",
            "substitutions": formatted_options
        }

    except Exception as e:
        logger.error(f"Substitution analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BARRY HARRIS DIMINISHED SYSTEM
# ============================================================================


@router.post("/barry-harris/sixth-diminished")
async def barry_harris_sixth_diminished(request: BarryHarrisRequest):
    """
    Generate Barry Harris 6th-diminished scale harmonization.

    Returns alternating 6 and dim7 chords with explanation.
    """
    try:
        # Generate 6th-diminished scale
        harmonization = get_sixth_diminished_scale(
            request.root,
            request.octave,
            request.prefer_sharps
        )

        # Generate AI explanation
        explanation_prompt = f"""Explain the Barry Harris 6th-diminished scale to an {request.student_level} student.

Root: {request.root}

Explain:
1. What the 6th-diminished scale is (8-note scale)
2. How it alternates between major 6 and diminished 7 chords
3. Why this is useful for bebop and jazz improvisation
4. How to practice using this scale

Be clear and educational (3-4 sentences)."""

        try:
            ai_response = await ai_orchestrator.generate_with_fallback(
                prompt=explanation_prompt,
                task_type=TaskType.THEORY_ANALYSIS,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                    "response_mime_type": "text/plain",
                }
            )
            explanation = ai_response if isinstance(ai_response, str) else ai_response.get("text", "")
        except Exception:
            explanation = "The 6th-diminished scale alternates between major 6 and diminished 7 chords."

        return {
            "root": request.root,
            "harmonization": [
                {
                    "symbol": chord[0],
                    "voicing": chord[1]
                }
                for chord in harmonization
            ],
            "ai_explanation": explanation
        }

    except Exception as e:
        logger.error(f"Barry Harris scale generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI THEORY COACH
# ============================================================================


class AICoachRequest(BaseModel):
    """Request for AI Theory Coach Q&A"""
    question: str = Field(..., description="Theory question from student")
    student_level: str = Field(default="intermediate", description="Student skill level")
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous conversation messages for context"
    )


@router.post("/ai-coach/ask")
async def ai_coach_ask(request: AICoachRequest):
    """
    Ask the AI Theory Coach a question about music theory.

    The AI adapts its explanation to the student's level and provides:
    - Clear concept explanations
    - Musical examples
    - Practice suggestions
    - Related concepts to explore

    Uses Qwen2.5-7B (complexity 6) for quality explanations while staying local/free.
    """
    try:
        # Build context-aware prompt
        context = ""
        if request.conversation_history:
            context = "\n\nPrevious conversation:\n"
            for msg in request.conversation_history[-3:]:  # Last 3 messages
                role = "Student" if msg["role"] == "user" else "Coach"
                context += f"{role}: {msg['content']}\n"

        prompt = f"""
        You are an expert music theory coach teaching a {request.student_level} level student.

        {context}

        Student Question: {request.question}

        Provide a clear, accurate answer that:
        1. Explains the concept at {request.student_level} level (adjust complexity accordingly)
        2. Includes a musical example if relevant (chord progression, scale, etc.)
        3. Suggests one related concept to explore next
        4. Uses encouraging, educational tone

        Keep the response concise (3-5 paragraphs max).
        """

        response = await ai_orchestrator.generate(
            task_type=TaskType.THEORY_EXPLANATION,
            prompt=prompt,
            complexity=6,  # Qwen2.5-7B (local, quality explanations)
            max_tokens=600
        )

        answer = response.get("text", "")

        # TODO: In future, parse musical examples from response and return structured data
        # For now, return plain text answer

        return {
            "answer": answer,
            "examples": [],  # Placeholder for future structured examples
            "related_concepts": [],  # Placeholder for future concept suggestions
            "student_level": request.student_level
        }

    except Exception as e:
        logger.error(f"AI Coach query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================


@router.get("/health")
async def health_check():
    """Health check for theory tools API"""
    return {
        "status": "healthy",
        "ai_available": ai_orchestrator.is_available(),
        "ai_status": ai_orchestrator.get_status()
    }
