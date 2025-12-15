# STORY-2.4: AI-Powered Performance Feedback Generation

**Epic**: EPIC-2 (Real-Time Performance Analysis)
**Status**: 📋 Planned
**Priority**: Must Have
**Effort**: 5 story points
**Dependencies**: STORY-2.1 (Pitch), STORY-2.2 (Rhythm)
**Target**: Week 4 of Phase 2

---

## User Story

**As a** piano student reviewing my practice session
**I want** personalized, actionable feedback on my performance
**So that** I know exactly what to improve and how to practice more effectively

## Acceptance Criteria

- [ ] Generate contextual feedback based on pitch, rhythm, and dynamics analysis
- [ ] Feedback is actionable (specific practice suggestions, not generic)
- [ ] Personalized to student skill level (beginner/intermediate/advanced)
- [ ] Response time <3 seconds using local Qwen2.5-7B (complexity 6-7)
- [ ] Structured output with categories: strengths, areas to improve, practice tips
- [ ] Fallback to Gemini Pro only if local generation fails
- [ ] Support multiple feedback styles (encouraging, technical, concise)
- [ ] Python API for backend integration
- [ ] Unit and integration tests

## Technical Specification

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Frontend (React)                         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Feedback Display Component                           │ │
│  │  - Strengths section (green)                         │ │
│  │  - Areas to improve (yellow)                         │ │
│  │  - Practice tips (blue)                              │ │
│  │  - Specific exercises generated                      │ │
│  └───────────────────────────┬────────────────────────────┘ │
└────────────────────────────┬─┘                              │
                             │ REST API
                             ↓
┌────────────────────────────────────────────────────────────┐
│                Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  FeedbackGenerator Service                            │ │
│  │                                                        │ │
│  │  async def generate_feedback(                        │ │
│  │      pitch_results: List[PitchResult],               │ │
│  │      rhythm_score: RhythmScore,                      │ │
│  │      dynamics_score: DynamicsScore,                  │ │
│  │      skill_level: SkillLevel,                        │ │
│  │      piece_name: str                                  │ │
│  │  ) -> PerformanceFeedback:                           │ │
│  │                                                        │ │
│  │      # 1. Aggregate analysis results                 │ │
│  │      summary = self._summarize_results(...)          │ │
│  │                                                        │ │
│  │      # 2. Build prompt with context                  │ │
│  │      prompt = self._build_feedback_prompt(           │ │
│  │          summary, skill_level, piece_name            │ │
│  │      )                                                 │ │
│  │                                                        │ │
│  │      # 3. Generate with local LLM (Qwen2.5-7B)      │ │
│  │      feedback = await ai_orchestrator.generate(      │ │
│  │          prompt=prompt,                              │ │
│  │          complexity=6,  # Use Qwen2.5-7B             │ │
│  │          response_format=FeedbackSchema              │ │
│  │      )                                                 │ │
│  │                                                        │ │
│  │      return feedback                                  │ │
│  │  }                                                     │ │
│  └───────────────────────────┬────────────────────────────┘ │
└────────────────────────────┬─┘                              │
                             │
                             ↓
┌────────────────────────────────────────────────────────────┐
│              AI Orchestrator (multi_model_service)         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Complexity 6-7 → Qwen2.5-7B (local)                 │ │
│  │  - 7B parameter model                                │ │
│  │  - ~3 second response time                           │ │
│  │  - Structured JSON output (Pydantic)                 │ │
│  │  - Cost-free (local inference via MLX)              │ │
│  │                                                        │ │
│  │  Fallback: Gemini Pro (cloud, only if local fails)  │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Data Structures

```python
# backend/app/schemas/feedback.py

from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class FeedbackCategory(str, Enum):
    PITCH = "pitch_accuracy"
    RHYTHM = "rhythm_timing"
    DYNAMICS = "dynamic_expression"
    TECHNIQUE = "playing_technique"
    MUSICALITY = "musical_interpretation"

class FeedbackItem(BaseModel):
    category: FeedbackCategory
    observation: str = Field(
        description="Specific observation about performance"
    )
    suggestion: str = Field(
        description="Actionable improvement suggestion"
    )
    priority: int = Field(
        ge=1, le=3,
        description="1=high priority, 3=low priority"
    )

class PracticeExercise(BaseModel):
    title: str
    description: str
    duration_minutes: int
    difficulty: SkillLevel

class PerformanceFeedback(BaseModel):
    overall_score: float = Field(
        ge=0, le=100,
        description="Overall performance score (0-100)"
    )
    summary: str = Field(
        description="2-3 sentence overall summary"
    )
    strengths: List[str] = Field(
        max_items=3,
        description="Top 3 strengths in this performance"
    )
    areas_to_improve: List[FeedbackItem] = Field(
        max_items=5,
        description="Specific areas needing improvement"
    )
    practice_exercises: List[PracticeExercise] = Field(
        max_items=3,
        description="Recommended practice exercises"
    )
    encouragement: str = Field(
        description="Motivational closing message"
    )

class AnalysisSummary(BaseModel):
    """Internal model for summarizing analysis results"""
    pitch_accuracy: float  # 0-100
    rhythm_accuracy: float  # 0-100
    dynamics_range: float  # dB
    tempo_stability: float  # 0-100
    common_pitch_errors: List[str]
    common_rhythm_errors: List[str]
    skill_level: SkillLevel
    piece_name: str
    piece_difficulty: str  # e.g., "Grade 3", "Beginner"
```

### Prompt Engineering

```python
# backend/app/services/feedback_generator.py

from app.services.ai_orchestrator import ai_orchestrator
from app.schemas.feedback import *

class FeedbackGenerator:
    def _build_feedback_prompt(
        self,
        summary: AnalysisSummary,
        style: str = "encouraging"
    ) -> str:
        """
        Build context-rich prompt for LLM feedback generation.
        """
        return f"""You are an expert piano teacher providing personalized feedback to a {summary.skill_level.value} student.

**Performance Analysis Summary:**
- Piece: {summary.piece_name} ({summary.piece_difficulty})
- Pitch Accuracy: {summary.pitch_accuracy:.1f}%
- Rhythm Accuracy: {summary.rhythm_accuracy:.1f}%
- Dynamic Range: {summary.dynamics_range:.1f} dB
- Tempo Stability: {summary.tempo_stability:.1f}%

**Common Errors Detected:**
Pitch: {', '.join(summary.common_pitch_errors) if summary.common_pitch_errors else 'None'}
Rhythm: {', '.join(summary.common_rhythm_errors) if summary.common_rhythm_errors else 'None'}

**Your Task:**
Generate constructive, actionable feedback for this student. Follow these guidelines:

1. **Be Specific**: Reference actual performance data (e.g., "Your rhythm accuracy of 87% shows improvement, but the rushed notes in bars 5-8...")
2. **Be Actionable**: Provide concrete practice steps (e.g., "Practice bars 5-8 with a metronome at 60 BPM")
3. **Be Encouraging**: Start with strengths, then areas to improve
4. **Match Skill Level**: Use appropriate terminology for a {summary.skill_level.value} student
5. **Prioritize**: Focus on 2-3 most important improvements (don't overwhelm)

**Tone**: {style} and supportive

Generate feedback in structured JSON format following the PerformanceFeedback schema.
"""

    async def generate_feedback(
        self,
        pitch_results: List[dict],
        rhythm_score: RhythmScore,
        dynamics_score: DynamicsScore,
        skill_level: SkillLevel = SkillLevel.INTERMEDIATE,
        piece_name: str = "practice exercise",
        piece_difficulty: str = "intermediate"
    ) -> PerformanceFeedback:
        """
        Generate AI-powered performance feedback.
        """
        # 1. Summarize analysis results
        summary = self._summarize_results(
            pitch_results,
            rhythm_score,
            dynamics_score,
            skill_level,
            piece_name,
            piece_difficulty
        )

        # 2. Build prompt
        prompt = self._build_feedback_prompt(summary)

        # 3. Generate with Qwen2.5-7B (complexity 6-7)
        try:
            response = await ai_orchestrator.generate(
                prompt=prompt,
                complexity=6,  # Qwen2.5-7B (local, cost-free)
                response_format=PerformanceFeedback,
                max_tokens=1500
            )

            return PerformanceFeedback.model_validate_json(response)

        except Exception as e:
            # Fallback: generic feedback if LLM fails
            return self._generate_fallback_feedback(summary)

    def _summarize_results(
        self,
        pitch_results: List[dict],
        rhythm_score: RhythmScore,
        dynamics_score: DynamicsScore,
        skill_level: SkillLevel,
        piece_name: str,
        piece_difficulty: str
    ) -> AnalysisSummary:
        """
        Aggregate analysis results into summary for LLM.
        """
        # Calculate pitch accuracy
        correct_pitches = sum(1 for p in pitch_results if p.get("is_correct", False))
        pitch_accuracy = (correct_pitches / len(pitch_results) * 100) if pitch_results else 0

        # Identify common pitch errors
        pitch_errors = []
        sharp_count = sum(1 for p in pitch_results if p.get("cents_offset", 0) > 20)
        flat_count = sum(1 for p in pitch_results if p.get("cents_offset", 0) < -20)

        if sharp_count > len(pitch_results) * 0.2:
            pitch_errors.append(f"{sharp_count} notes played sharp")
        if flat_count > len(pitch_results) * 0.2:
            pitch_errors.append(f"{flat_count} notes played flat")

        # Identify common rhythm errors
        rhythm_errors = []
        if rhythm_score.early_notes > rhythm_score.on_time_notes * 0.3:
            rhythm_errors.append(f"{rhythm_score.early_notes} notes rushed")
        if rhythm_score.late_notes > rhythm_score.on_time_notes * 0.3:
            rhythm_errors.append(f"{rhythm_score.late_notes} notes dragged")
        if abs(rhythm_score.tempo_drift) > 10:
            direction = "faster" if rhythm_score.tempo_drift > 0 else "slower"
            rhythm_errors.append(f"Tempo drifted {abs(rhythm_score.tempo_drift):.1f}% {direction}")

        # Calculate tempo stability
        tempo_stability = max(0, 100 - abs(rhythm_score.tempo_drift))

        return AnalysisSummary(
            pitch_accuracy=pitch_accuracy,
            rhythm_accuracy=rhythm_score.accuracy_percent,
            dynamics_range=dynamics_score.dynamic_range_db,
            tempo_stability=tempo_stability,
            common_pitch_errors=pitch_errors,
            common_rhythm_errors=rhythm_errors,
            skill_level=skill_level,
            piece_name=piece_name,
            piece_difficulty=piece_difficulty
        )

    def _generate_fallback_feedback(self, summary: AnalysisSummary) -> PerformanceFeedback:
        """
        Generate basic rule-based feedback if LLM fails.
        """
        overall = (summary.pitch_accuracy + summary.rhythm_accuracy) / 2

        strengths = []
        improvements = []

        if summary.pitch_accuracy >= 85:
            strengths.append("Excellent pitch accuracy")
        else:
            improvements.append(FeedbackItem(
                category=FeedbackCategory.PITCH,
                observation=f"Pitch accuracy is {summary.pitch_accuracy:.1f}%",
                suggestion="Practice scales slowly with a tuner",
                priority=1
            ))

        if summary.rhythm_accuracy >= 85:
            strengths.append("Strong rhythmic precision")
        else:
            improvements.append(FeedbackItem(
                category=FeedbackCategory.RHYTHM,
                observation=f"Rhythm accuracy is {summary.rhythm_accuracy:.1f}%",
                suggestion="Use a metronome, starting at slower tempo",
                priority=1
            ))

        return PerformanceFeedback(
            overall_score=overall,
            summary=f"You scored {overall:.1f}% overall on {summary.piece_name}.",
            strengths=strengths or ["You completed the piece!"],
            areas_to_improve=improvements,
            practice_exercises=[
                PracticeExercise(
                    title="Slow Practice",
                    description="Practice at 50% tempo with metronome",
                    duration_minutes=10,
                    difficulty=summary.skill_level
                )
            ],
            encouragement="Keep practicing, you're making progress!"
        )
```

### API Endpoint

```python
# backend/app/api/routes/analysis.py

@router.post("/feedback/generate")
async def generate_performance_feedback(
    pitch_results: List[dict],
    rhythm_score: RhythmScore,
    dynamics_score: DynamicsScore,
    skill_level: SkillLevel = SkillLevel.INTERMEDIATE,
    piece_name: str = "practice exercise"
) -> PerformanceFeedback:
    """
    Generate AI-powered feedback for a practice session.

    Args:
        pitch_results: Pitch detection results
        rhythm_score: Rhythm analysis score
        dynamics_score: Dynamics analysis score
        skill_level: Student skill level
        piece_name: Name of piece practiced

    Returns:
        Structured feedback with strengths, improvements, exercises
    """
    generator = FeedbackGenerator()

    feedback = await generator.generate_feedback(
        pitch_results=pitch_results,
        rhythm_score=rhythm_score,
        dynamics_score=dynamics_score,
        skill_level=skill_level,
        piece_name=piece_name
    )

    return feedback
```

---

## Implementation Plan

### Phase 1: Prompt Engineering (Days 1-2)

- [ ] Design prompt template with context injection
- [ ] Define PerformanceFeedback schema
- [ ] Test prompts with Qwen2.5-7B
- [ ] Refine based on output quality
- [ ] Document prompt best practices

### Phase 2: Feedback Service (Days 3-4)

- [ ] Implement `FeedbackGenerator` service
- [ ] Implement `_summarize_results()` aggregation
- [ ] Implement `_build_feedback_prompt()`
- [ ] Integrate with `ai_orchestrator`
- [ ] Implement fallback feedback (rule-based)
- [ ] Write unit tests

### Phase 3: API & Testing (Day 5)

- [ ] Create `/feedback/generate` endpoint
- [ ] Write integration tests
- [ ] Test with real analysis data
- [ ] Validate response quality (manual review)
- [ ] Document API usage

---

## Testing Strategy

### Unit Tests

```python
@pytest.mark.asyncio
async def test_feedback_generation():
    generator = FeedbackGenerator()

    # Mock analysis results
    pitch_results = [{"is_correct": True, "cents_offset": 5}] * 18 + [{"is_correct": False, "cents_offset": 30}] * 2
    rhythm_score = RhythmScore(
        accuracy_percent=87.5,
        on_time_notes=14,
        early_notes=3,
        late_notes=3,
        tempo_drift=5.2
    )
    dynamics_score = DynamicsScore(
        dynamic_range_db=24.5,
        expression_score=65.3
    )

    feedback = await generator.generate_feedback(
        pitch_results,
        rhythm_score,
        dynamics_score,
        SkillLevel.INTERMEDIATE,
        "C Major Scale"
    )

    # Validate structure
    assert 0 <= feedback.overall_score <= 100
    assert len(feedback.strengths) > 0
    assert len(feedback.areas_to_improve) > 0
    assert len(feedback.practice_exercises) > 0
    assert len(feedback.summary) > 20  # Not empty

@pytest.mark.asyncio
async def test_feedback_response_time():
    generator = FeedbackGenerator()

    import time
    start = time.perf_counter()

    # Generate feedback
    await generator.generate_feedback([], mock_rhythm, mock_dynamics)

    duration = time.perf_counter() - start

    assert duration < 3.0, f"Feedback took {duration}s, target <3s"
```

---

## Performance Requirements

| Metric | Target |
|--------|--------|
| Response time (Qwen2.5-7B) | <3 seconds |
| Feedback quality (human eval) | >4.0/5.0 rating |
| Actionability score | >80% (feedback includes specific steps) |
| Personalization accuracy | Matches skill level 90%+ of time |

---

## Definition of Done

- [ ] Code merged to `develop`
- [ ] All tests passing
- [ ] Feedback quality validated (10+ manual reviews >4.0/5.0)
- [ ] Response time <3s on M4
- [ ] API documented
- [ ] Code reviewed

---

**Created**: 2025-12-15
**Assigned To**: AI/Backend Team
