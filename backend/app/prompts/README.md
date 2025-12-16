# AI Prompt Architecture - Usage Guide

This module provides a comprehensive prompt management system with genre-authentic system prompts, rich context building, and silent fallback with developer logging.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Genre-Authentic Prompts](#genre-authentic-prompts)
5. [PromptBuilder Usage](#promptbuilder-usage)
6. [Metadata Tracking](#metadata-tracking)
7. [Testing](#testing)
8. [Best Practices](#best-practices)

---

## Overview

### Design Philosophy

**Quality over Brevity**: Prompts prioritize rich context over token minimization to maximize educational content quality.

**Genre Authenticity**: Each musical genre (Gospel, Jazz, Blues, Classical, Neo-Soul) has deeply authentic system prompts with cultural context and proper terminology.

**Silent Fallback**: Users see seamless experiences; developers get full visibility into failures.

**Attribution-Free**: No citation requirements for cleaner user experience.

### Key Features

- ✅ **Genre-specific system prompts** with cultural context
- ✅ **Structured prompt building** with fluent API
- ✅ **Generation metadata tracking** for monitoring
- ✅ **Silent fallback chain** (Local LLM → Gemini → Template)
- ✅ **Developer logging** for full transparency
- ✅ **Health metrics** for dashboard monitoring

---

## Quick Start

### Basic Tutorial Generation

```python
from app.prompts.builders import TutorialPromptBuilder
from app.services.ai_orchestrator_enhanced import enhanced_ai_orchestrator, TaskType

# Build genre-authentic prompt
builder = TutorialPromptBuilder(genre="gospel")
builder.add_lesson_content(
    title="Gospel Voicings 101",
    concepts=["Shell voicings", "Added 9ths", "Upper structure triads"],
    difficulty="intermediate"
)
builder.add_student_profile(
    skill_level="intermediate",
    technical_ability=6,
    theory_knowledge=5
)

prompt = builder.build()

# Generate with metadata tracking
result = await enhanced_ai_orchestrator.generate_with_metadata(
    prompt=prompt,
    task_type=TaskType.TUTORIAL_GENERATION,
    complexity=7,  # Llama 3.3 70B (local, GPT-4 quality)
    genre="gospel",
    return_metadata=False  # Users see only content
)

# Result is seamless - no error messages even if AI fails
```

### Basic Feedback Generation

```python
from app.prompts.builders import FeedbackPromptBuilder

# Build feedback prompt
builder = FeedbackPromptBuilder(genre="jazz")
builder.add_performance_data(
    pitch_accuracy=78.5,
    rhythm_accuracy=82.0,
    tempo_stability=75.0,
    common_errors={
        "pitch": ["Missed Bb in bar 5", "Sharp on F#"],
        "rhythm": ["Rushed eighth notes in bar 8"]
    }
)
builder.add_student_profile(
    skill_level="intermediate",
    technical_ability=6
)

prompt = builder.build()

# Generate feedback
feedback = await enhanced_ai_orchestrator.generate_with_metadata(
    prompt=prompt,
    task_type=TaskType.TUTORIAL_GENERATION,  # Use appropriate task type
    complexity=6,  # Qwen2.5-7B (local)
    genre="jazz"
)
```

---

## Core Components

### 1. System Prompts (`system_prompts.py`)

Contains genre-specific and task-specific system prompts.

#### Genre System Prompts

```python
from app.prompts.system_prompts import GENRE_SYSTEM_PROMPTS, get_system_prompt

# Get gospel system prompt
gospel_prompt = GENRE_SYSTEM_PROMPTS["gospel"]

# Get combined prompt (genre + task)
full_prompt = get_system_prompt(
    task_type="tutorial",
    genre="gospel",
    include_genre=True
)
```

**Available Genres:**
- `gospel` - Black church tradition, Sunday morning sound
- `jazz` - Bebop through modern jazz, standards-based
- `blues` - Delta, Chicago, Texas blues, boogie-woogie
- `classical` - Baroque through Contemporary, period styles
- `neosoul` - R&B, funk, jazz fusion, modern soul

#### Task System Prompts

```python
from app.prompts.system_prompts import TASK_SYSTEM_PROMPTS

# Available task types
tutorial_prompt = TASK_SYSTEM_PROMPTS["tutorial"]
feedback_prompt = TASK_SYSTEM_PROMPTS["feedback"]
exercise_prompt = TASK_SYSTEM_PROMPTS["exercise"]
curriculum_prompt = TASK_SYSTEM_PROMPTS["curriculum"]
```

### 2. Prompt Builders (`builders.py`)

Fluent API for constructing structured prompts.

#### Base PromptBuilder

```python
from app.prompts.builders import PromptBuilder

builder = PromptBuilder(task_type="tutorial", genre="jazz")

# Chain methods fluently
builder \
    .add_context("Lesson Info", {
        "title": "ii-V-I Progressions",
        "difficulty": "intermediate"
    }) \
    .add_student_profile(
        skill_level="intermediate",
        technical_ability=6
    ) \
    .add_requirements([
        "Include chord-scale relationships",
        "Reference jazz standards",
        "Provide listening examples"
    ]) \
    .add_output_format("JSON", {
        "overview": "2-3 sentence introduction",
        "concepts": "List of core concepts",
        "practice_steps": "Step-by-step practice guidance"
    })

prompt = builder.build()
token_estimate = builder.get_token_estimate()  # Rough token count
```

#### Specialized Builders

```python
from app.prompts.builders import (
    TutorialPromptBuilder,
    FeedbackPromptBuilder,
    ExercisePromptBuilder,
    CurriculumPromptBuilder
)

# Tutorial builder (includes tutorial-specific requirements)
tutorial_builder = TutorialPromptBuilder(genre="gospel")

# Feedback builder (includes feedback-specific output format)
feedback_builder = FeedbackPromptBuilder(genre="blues")

# Exercise builder (includes exercise-specific requirements)
exercise_builder = ExercisePromptBuilder(genre="classical")

# Curriculum builder (includes curriculum-specific structure)
curriculum_builder = CurriculumPromptBuilder(genre="neosoul")
```

### 3. Metadata Tracking (`metadata.py`)

Track generation results for monitoring.

#### GenerationMetadata

```python
from app.prompts.metadata import GenerationMetadata, ModelSource

metadata = GenerationMetadata(
    model_used=ModelSource.LLAMA_3_3_70B,
    fallback_count=0,
    generation_time_ms=2345.67,
    token_count=1250,
    quality_confidence=0.95,
    complexity=7,
    error_chain=[]
)

# Check quality
print(metadata.model_used)  # "llama-3.3-70b"
print(metadata.quality_confidence)  # 0.95
```

#### GenerationResult

```python
from app.prompts.metadata import GenerationResult

result = GenerationResult(
    content={"tutorial": "..."},
    metadata=metadata
)

# For users (no metadata shown)
user_response = result.to_user_response()
# Returns: {"tutorial": "..."}

# For admins/devs (full context)
admin_response = result.to_admin_response()
# Returns: {
#   "content": {"tutorial": "..."},
#   "meta": {
#     "model": "llama-3.3-70b",
#     "fallbacks": 0,
#     "quality_confidence": 0.95,
#     ...
#   }
# }

# Helper methods
print(result.has_fallback())  # False
print(result.is_template_based())  # False
print(result.get_quality_tier())  # "excellent"
```

---

## Genre-Authentic Prompts

### Gospel System Prompt

**Characteristics:**
- Deep roots in Black church tradition
- Emphasis on "Sunday morning sound"
- Shell voicings with color tones (9ths, 11ths)
- Chromatic runs and approach notes
- Spiritual and emotional context

**Key Terminology:**
- "Sunday morning chord" - Maj7(9) spacious voicing
- "Shout feel" - Repeated V-I with intensity
- "Run transition" - Chromatic approach notes
- "Praise break" - Suspended build to resolution

**Example:**
```python
builder = TutorialPromptBuilder(genre="gospel")
# Automatically includes gospel-specific context:
# - Voicing techniques (shell voicings, cluster chords)
# - Cultural significance (worship, congregation)
# - Authentic patterns (runs, shouts, transitions)
```

### Jazz System Prompt

**Characteristics:**
- Rooted in bebop through contemporary jazz
- Extensions and alterations as essential colors
- ii-V-I foundation with substitutions
- References to standards and recordings
- Historical lineage (Miles, Coltrane, Evans)

**Key Terminology:**
- "Comping" - Chord accompaniment
- "Changes" - Chord progression
- "Guide tones" - 3rds and 7ths defining harmony
- "Shell voicing" - Root, 3rd, 7th foundation

**Example:**
```python
builder = TutorialPromptBuilder(genre="jazz")
# Includes jazz-specific context:
# - Chord-scale theory
# - Voice leading with guide tones
# - References to Real Book standards
# - Historical performance practice
```

### Blues System Prompt

**Characteristics:**
- Delta, Chicago, Texas traditions
- 12-bar blues with variations
- Left-hand patterns (boogie-woogie, walking bass)
- Expressive techniques (bends, vibrato, grit)
- Space and emotional authenticity

**Key Terminology:**
- "Blue note" - Flattened 5th
- "Turnaround" - I-VI-ii-V back to top
- "Shuffle" - Swung eighth note feel
- "Crushed note" - Chromatic grace note

### Classical System Prompt

**Characteristics:**
- Baroque through Contemporary periods
- Functional harmony and voice leading
- Proper technique and posture
- Period-appropriate style and interpretation
- Italian/German terminology

**Key Terminology:**
- Tempo: Allegro, Andante, Adagio
- Dynamics: Piano, forte, crescendo
- Articulation: Legato, staccato, tenuto
- Expression: Cantabile, dolce, espressivo

### Neo-Soul System Prompt

**Characteristics:**
- Modern R&B, funk, jazz fusion
- Extended harmony (9ths, 11ths, 13ths)
- Laid-back groove, behind-the-beat feel
- Rhodes/Wurlitzer aesthetic
- References to D'Angelo, Glasper, H.E.R.

**Key Terminology:**
- "Pocket" - Locked-in rhythmic groove
- "Vamp" - Repeated progression for improvisation
- "Texture" - Layered sounds and timbres
- "Rhodes sound" - Classic electric piano tone

---

## PromptBuilder Usage

### Method Chaining

```python
prompt = (
    TutorialPromptBuilder(genre="gospel")
    .add_lesson_content(
        title="Gospel Voicings",
        concepts=["Shell voicings", "Added 9ths"],
        duration_minutes=45
    )
    .add_student_profile(
        skill_level="intermediate",
        technical_ability=6,
        goals=["Master church comping", "Learn gospel runs"]
    )
    .add_requirements([
        "Reference Sunday morning worship context",
        "Include authentic gospel terminology",
        "Provide practice tips for church setting"
    ])
    .build()
)
```

### Custom Sections

```python
builder = PromptBuilder(task_type="tutorial", genre="jazz")

builder.add_custom_section(
    "Historical Context",
    """
    This lesson builds on bebop tradition, particularly the innovations
    of Charlie Parker and Dizzy Gillespie in the 1940s. We'll explore
    how Bill Evans later adapted these concepts for piano.
    """
)

builder.add_custom_section(
    "Listening Examples",
    """
    Essential recordings:
    - Bill Evans - "Waltz for Debby" (1961)
    - McCoy Tyner - "The Real McCoy" (1967)
    - Herbie Hancock - "Maiden Voyage" (1965)
    """
)
```

### Performance Data

```python
builder = FeedbackPromptBuilder(genre="blues")

builder.add_performance_data(
    pitch_accuracy=75.5,
    rhythm_accuracy=82.0,
    tempo_stability=70.0,
    dynamics_range=12.5,
    common_errors={
        "pitch": ["Missed blue note in bar 3"],
        "rhythm": ["Shuffle feel inconsistent", "Rushed turnaround"]
    }
)
```

---

## Metadata Tracking

### Generation Workflow

```python
# Generate with metadata
result = await enhanced_ai_orchestrator.generate_with_metadata(
    prompt=prompt,
    task_type=TaskType.TUTORIAL_GENERATION,
    complexity=7,
    genre="gospel",
    return_metadata=True  # Get full GenerationResult
)

# Access metadata
print(f"Model: {result.metadata.model_used}")
print(f"Time: {result.metadata.generation_time_ms}ms")
print(f"Fallbacks: {result.metadata.fallback_count}")
print(f"Quality: {result.metadata.quality_confidence}")

# Check fallback status
if result.has_fallback():
    print("⚠️ This generation used fallback")
    print(f"Error chain: {result.metadata.error_chain}")

if result.is_template_based():
    print("🚨 This generation used template (all AI failed)")
```

### Health Metrics

```python
from app.services.ai_orchestrator_enhanced import enhanced_ai_orchestrator

# Get health metrics for dashboard
metrics = enhanced_ai_orchestrator.get_health_metrics()

print(f"Total requests: {metrics.total_requests}")
print(f"Fallback rate: {metrics.fallback_rate * 100:.1f}%")
print(f"Template rate: {metrics.template_count / metrics.total_requests * 100:.1f}%")

# By task type
for task_type, rate in metrics.by_task_type.items():
    print(f"{task_type}: {rate * 100:.1f}% fallback")

# By genre
for genre, rate in metrics.by_genre.items():
    print(f"{genre}: {rate * 100:.1f}% fallback")

# Recent failures
for failure in metrics.recent_failures:
    print(f"Failed: {failure['task_type']} (complexity {failure['complexity']})")
    print(f"Errors: {failure['error_chain']}")
```

---

## Testing

### Unit Testing Prompts

```python
import pytest
from app.prompts.builders import TutorialPromptBuilder

def test_gospel_tutorial_prompt():
    builder = TutorialPromptBuilder(genre="gospel")
    builder.add_lesson_content(
        title="Test Lesson",
        concepts=["Concept 1", "Concept 2"]
    )

    prompt = builder.build()

    # Verify gospel context included
    assert "gospel" in prompt.lower()
    assert "Sunday morning" in prompt or "church" in prompt

    # Verify structure
    assert "Test Lesson" in prompt
    assert "Concept 1" in prompt

def test_token_estimation():
    builder = TutorialPromptBuilder(genre="jazz")
    builder.add_lesson_content(title="Short lesson")

    tokens = builder.get_token_estimate()
    assert tokens > 0
    assert tokens < 10000  # Reasonable upper bound
```

### Integration Testing

```python
import pytest
from app.services.tutorial_service_enhanced import EnhancedTutorialService

@pytest.mark.asyncio
async def test_tutorial_generation_with_fallback():
    service = EnhancedTutorialService()

    # Mock lesson
    lesson = MockLesson(
        id=1,
        title="Test Lesson",
        description="Test description",
        concepts_json='["Concept 1"]',
        week_number=1
    )

    # Generate tutorial
    tutorial = await service.generate_lesson_tutorial(
        lesson=lesson,
        genre="gospel"
    )

    # Verify structure (even if fallback used)
    assert "overview" in tutorial
    assert "concepts" in tutorial
    assert "practice_steps" in tutorial
    assert "encouragement" in tutorial
```

---

## Best Practices

### 1. Choose Appropriate Complexity

```python
# Simple tasks (Phi-3.5 Mini, complexity 1-4)
- Exercise validation
- Simple tips generation
- Content categorization

# Moderate tasks (Llama 3.3 70B, complexity 5-7)
- Tutorial generation
- Feedback generation
- Theory explanations

# Complex tasks (Gemini Pro, complexity 8-10)
- Curriculum planning
- Creative composition
- Advanced analysis
```

### 2. Use Genre Context Appropriately

```python
# ✅ GOOD: Genre specified for stylistic content
tutorial = await service.generate_lesson_tutorial(
    lesson=lesson,
    genre="gospel"  # Ensures gospel-authentic language
)

# ❌ AVOID: Generic generation for genre-specific content
tutorial = await service.generate_lesson_tutorial(
    lesson=gospel_lesson,
    genre=None  # Loses cultural authenticity
)
```

### 3. Return Metadata Only for Admin/Dev

```python
# For users (clean, seamless)
result = await orchestrator.generate_with_metadata(
    prompt=prompt,
    task_type=task_type,
    return_metadata=False  # ← Users see only content
)

# For admins/devs (full context)
result = await orchestrator.generate_with_metadata(
    prompt=prompt,
    task_type=task_type,
    return_metadata=True  # ← Devs see metadata
)
```

### 4. Log Appropriately

```python
# ✅ GOOD: Structured logging with extra context
logger.info(
    "Generated tutorial successfully",
    extra={
        "lesson_id": lesson.id,
        "genre": genre,
        "complexity": complexity,
        "generation_time_ms": time_ms
    }
)

# ❌ AVOID: Generic logs without context
logger.info("Tutorial generated")
```

### 5. Handle Fallbacks Gracefully

```python
# Your code doesn't need to check for fallbacks
# The orchestrator handles it silently

tutorial = await service.generate_lesson_tutorial(lesson, genre="jazz")

# This ALWAYS succeeds (template fallback guaranteed)
# Users never see error messages
# Developers see full error chain in logs
```

---

## Migration Guide

### Old Approach (String Concatenation)

```python
# OLD WAY ❌
prompt = f"""Generate a comprehensive piano lesson tutorial in JSON format.

Lesson Information:
- Title: {lesson.title}
- Description: {lesson.description or 'Not provided'}
- Week Number: {lesson.week_number}
...
"""
```

### New Approach (PromptBuilder)

```python
# NEW WAY ✅
from app.prompts.builders import TutorialPromptBuilder

builder = TutorialPromptBuilder(genre="gospel")
builder.add_lesson_content(
    title=lesson.title,
    description=lesson.description,
    week_number=lesson.week_number
)
prompt = builder.build()
```

### Benefits of Migration

1. **Genre authenticity** - Automatic cultural context
2. **Structured building** - Cleaner, more maintainable code
3. **Token estimation** - Monitor prompt sizes
4. **Consistency** - Same format across all services
5. **Extensibility** - Easy to add new sections

---

## Examples

See `tutorial_service_enhanced.py` for complete working example.

## Support

Questions? Check the inline documentation in:
- `system_prompts.py` - Genre and task prompts
- `builders.py` - PromptBuilder API
- `metadata.py` - Metadata tracking
- `ai_orchestrator_enhanced.py` - Orchestration logic
