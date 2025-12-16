# Advanced Generator Features Guide

This guide documents the advanced features available through generator mixins. These features can be added to any genre generator via multiple inheritance.

## Table of Contents

1. [Overview](#overview)
2. [ML Progression Prediction](#ml-progression-prediction)
3. [Streaming Generation](#streaming-generation)
4. [Genre Fusion](#genre-fusion)
5. [User Preference Learning](#user-preference-learning)
6. [Advanced Analytics](#advanced-analytics)
7. [Usage Examples](#usage-examples)
8. [Best Practices](#best-practices)

---

## Overview

The advanced features are implemented as **mixins** - Python classes that add functionality via multiple inheritance. This design allows you to:

- **Pick and choose**: Add only the features you need
- **Zero overhead**: Unused features don't affect performance
- **Composable**: Combine multiple mixins together
- **Maintainable**: Each mixin is independently tested

### Available Mixins

| Mixin | Purpose | Use Case |
|-------|---------|----------|
| `MLProgressionPredictorMixin` | ML-powered chord prediction | Suggest next chords based on patterns |
| `StreamingGenerationMixin` | Real-time progressive generation | Stream bars as they're created |
| `GenreFusionMixin` | Multi-genre blending | Combine characteristics from genres |
| `UserPreferenceLearningMixin` | Personalization | Learn and adapt to user preferences |
| `AdvancedAnalyticsMixin` | Deep insights and metrics | Track quality, performance, trends |

---

## ML Progression Prediction

**File**: `app/services/advanced_generator_mixins.py`
**Class**: `MLProgressionPredictorMixin`

### Purpose

Uses machine learning (collaborative filtering + music theory rules) to predict the next chord(s) in a progression based on:
1. What similar users have played
2. Popular continuations
3. Music theory principles

### Key Methods

#### `predict_next_chord(current_progression, user_id, top_k=5)`

Predict the most likely next chord(s).

**Parameters**:
- `current_progression` (List[str]): Current chord sequence
- `user_id` (str): User identifier for personalization
- `top_k` (int): Number of predictions to return

**Returns**: List of (chord, probability) tuples

**Example**:
```python
from app.services.advanced_generator_mixins import MLProgressionPredictorMixin
from app.services.gospel_generator_refactored import GospelGeneratorService

class MLGospelGenerator(MLProgressionPredictorMixin, GospelGeneratorService):
    pass

generator = MLGospelGenerator()

# Predict next chord
predictions = generator.predict_next_chord(
    current_progression=["Cmaj7", "Am7", "Dm7"],
    user_id="user_123",
    top_k=5
)

# Output: [("G7", 0.45), ("Em7", 0.25), ("Fmaj7", 0.15), ...]
for chord, prob in predictions:
    print(f"{chord}: {prob*100:.1f}% confidence")
```

#### `record_progression(user_id, progression, metadata)`

Record a user's progression for ML training.

**Parameters**:
- `user_id` (str): User identifier
- `progression` (List[str]): Chord progression
- `metadata` (dict): Additional context (key, tempo, rating, etc.)

**Example**:
```python
generator.record_progression(
    user_id="user_123",
    progression=["Cmaj7", "Am7", "Dm7", "G7"],
    metadata={"key": "C", "tempo": 72, "rating": 5.0}
)
```

### Algorithm

The prediction combines three approaches:

1. **Collaborative Filtering**: "Users who played X also played Y"
   - Builds user similarity matrix
   - Recommends based on similar users' patterns

2. **Popularity-Based**: "Most common continuations"
   - Tracks frequency of chord sequences
   - Higher weight for frequently used progressions

3. **Theory-Based**: "What makes musical sense"
   - Circle of fifths relationships
   - Common functional progressions (ii-V-I, IV-V-I)
   - Genre-specific patterns

### Use Cases

- **Autocomplete**: Suggest chords as user builds progression
- **Learning**: Show students common continuations
- **Inspiration**: Offer creative alternatives
- **Validation**: Flag unusual progressions

---

## Streaming Generation

**File**: `app/services/advanced_generator_mixins.py`
**Class**: `StreamingGenerationMixin`

### Purpose

Generate arrangements progressively, yielding bars in real-time as they're created. Enables:
- Progressive loading in UI
- Cancellable generation
- Immediate playback feedback
- Reduced perceived latency

### Key Methods

#### `generate_streaming(request, callback=None)`

Generate arrangement with real-time streaming.

**Parameters**:
- `request`: Generation request object
- `callback` (optional): Function called for each event

**Yields**: Dictionary events with type and data

**Event Types**:
1. `metadata`: Initial info (key, tempo, chords)
2. `bar`: Individual bar completion
3. `complete`: Generation finished

**Example**:
```python
from app.services.advanced_generator_mixins import StreamingGenerationMixin
from app.services.gospel_generator_refactored import GospelGeneratorService
from app.models.gospel import GenerateGospelRequest

class StreamingGospelGenerator(StreamingGenerationMixin, GospelGeneratorService):
    pass

generator = StreamingGospelGenerator()

request = GenerateGospelRequest(
    description="Uplifting worship song",
    num_bars=8,
    include_progression=False
)

# Stream generation
async for event in generator.generate_streaming(request):
    if event["type"] == "metadata":
        print(f"Key: {event['key']}, Tempo: {event['tempo']}")
        print(f"Chords: {' | '.join(event['chords'])}")

    elif event["type"] == "bar":
        bar_num = event["bar_number"] + 1
        notes = event["notes"]
        print(f"Bar {bar_num} ready: {len(notes)} notes")

        # Send to frontend immediately
        await websocket.send(json.dumps(event))

    elif event["type"] == "complete":
        print(f"Complete! {event['total_bars']} bars generated")
```

### Implementation Details

Each bar is generated independently and yielded immediately:

```python
async def generate_streaming(self, request, callback=None):
    # 1. Yield metadata first
    yield {"type": "metadata", "key": key, "tempo": tempo, "chords": chords}

    # 2. Generate and yield bars progressively
    for bar_idx, chord in enumerate(chords):
        bar_arrangement = await self._generate_single_bar(chord, key, tempo, bar_idx)

        # Yield as soon as ready
        yield {
            "type": "bar",
            "bar_number": bar_idx,
            "notes": get_notes_preview(bar_arrangement, bars=1),
            "midi_preview": export_bar_to_base64(bar_arrangement)
        }

    # 3. Yield completion
    yield {"type": "complete", "total_bars": len(chords)}
```

### Use Cases

- **Long generations**: 16+ bar progressions
- **User feedback**: Show progress during generation
- **Cancellation**: User can stop if not satisfied
- **Preview**: Play first bars while rest generates

---

## Genre Fusion

**File**: `app/services/advanced_generator_mixins.py`
**Class**: `GenreFusionMixin`

### Purpose

Blend characteristics from multiple genres to create fusion styles. Examples:
- Gospel + Jazz = Gospel Jazz
- Latin + R&B = Latin R&B
- Blues + Gospel = Gospel Blues

### Key Methods

#### `generate_fusion(request, secondary_genre_generator, primary_weight=0.6)`

Generate fusion arrangement blending two genres.

**Parameters**:
- `request`: Generation request
- `secondary_genre_generator`: Second generator to blend
- `primary_weight` (float): Weight for primary genre (0.0-1.0)

**Returns**: Fusion arrangement

**Example**:
```python
from app.services.advanced_generator_mixins import GenreFusionMixin
from app.services.gospel_generator_refactored import gospel_generator_service
from app.services.jazz_generator_refactored import jazz_generator_service
from app.models.gospel import GenerateGospelRequest

# Enable fusion on gospel generator
class FusionGospelGenerator(GenreFusionMixin, GospelGeneratorService):
    pass

gospel_gen = FusionGospelGenerator()

request = GenerateGospelRequest(
    description="Spiritual ballad",
    num_bars=8
)

# Blend Gospel (70%) + Jazz (30%)
fusion = await gospel_gen.generate_fusion(
    request=request,
    secondary_genre_generator=jazz_generator_service,
    primary_weight=0.7
)

# Result: Gospel chord progressions with jazz voicing techniques
```

#### `get_fusion_suggestions()`

Get compatible genres for fusion.

**Returns**: List of (genre_name, compatibility_score) tuples

**Example**:
```python
suggestions = gospel_gen.get_fusion_suggestions()

# Output: [("Jazz", 0.9), ("Blues", 0.85), ("Neo-Soul", 0.8), ...]
for genre, score in suggestions:
    print(f"{genre}: {score*100:.0f}% compatible")
```

### Blending Algorithm

The fusion process blends:

1. **Harmonic Structure** (Primary)
   - Chord progression from primary genre
   - Extensions from secondary genre

2. **Voicing Techniques** (Secondary)
   - Voice leading rules from secondary
   - Spacing from secondary

3. **Rhythmic Feel** (Weighted Average)
   - Groove combines both genres
   - Articulation blended

**Weight Distribution**:
- 70/30: Primary dominant, subtle secondary influence
- 60/40: Balanced fusion
- 50/50: Equal blend

### Use Cases

- **Creative exploration**: Discover new sounds
- **Style evolution**: Modernize traditional genres
- **Education**: Teach genre relationships
- **Unique arrangements**: Differentiate from competitors

---

## User Preference Learning

**File**: `app/services/advanced_generator_mixins.py`
**Class**: `UserPreferenceLearningMixin`

### Purpose

Learn user preferences over time and personalize generation. Tracks:
- Ratings and feedback
- Replays and downloads
- Skips and deletions
- Tempo, key, mood preferences

### Key Methods

#### `record_user_feedback(user_id, generation_id, feedback_type, feedback_value, metadata)`

Record user interaction for learning.

**Parameters**:
- `user_id` (str): User identifier
- `generation_id` (str): Generated arrangement ID
- `feedback_type` (str): Type of feedback (rating, replay, download, skip)
- `feedback_value` (float): Numerical value (1-5 for rating, 1.0 for binary)
- `metadata` (dict): Context (tempo, key, mood, etc.)

**Example**:
```python
from app.services.advanced_generator_mixins import UserPreferenceLearningMixin
from app.services.gospel_generator_refactored import GospelGeneratorService

class PersonalizedGospelGenerator(UserPreferenceLearningMixin, GospelGeneratorService):
    pass

generator = PersonalizedGospelGenerator()

# User rates a generation highly
generator.record_user_feedback(
    user_id="user_456",
    generation_id="gen_001",
    feedback_type="rating",
    feedback_value=5.0,
    metadata={"tempo": 120, "key": "C", "mood": "uplifting"}
)

# User replays (positive signal)
generator.record_user_feedback(
    user_id="user_456",
    generation_id="gen_001",
    feedback_type="replay",
    feedback_value=1.0,
    metadata={"tempo": 120, "key": "C"}
)

# User skips (negative signal)
generator.record_user_feedback(
    user_id="user_456",
    generation_id="gen_002",
    feedback_type="skip",
    feedback_value=1.0,
    metadata={"tempo": 60, "key": "Am", "mood": "somber"}
)
```

#### `personalize_request(user_id, base_request)`

Adjust request based on learned preferences.

**Parameters**:
- `user_id` (str): User identifier
- `base_request`: Original request object

**Returns**: Personalized request

**Example**:
```python
base_request = GenerateGospelRequest(
    description="Worship song",
    num_bars=8
)

# Personalize based on user history
personalized = generator.personalize_request("user_456", base_request)

# System adjusts:
# - Tempo → ~120 BPM (user prefers uptempo)
# - Key → C major (user's favorite)
# - Mood → Uplifting (high-rated mood)
```

#### `get_user_profile(user_id)`

Get user's learned preferences.

**Returns**: Dictionary with profile data

**Example**:
```python
profile = generator.get_user_profile("user_456")

print(f"Total interactions: {profile['total_interactions']}")
print(f"Average rating: {profile['average_rating']:.1f}/5.0")
print(f"Preferred tempo: {profile['preferences']['tempo']}")
print(f"Preferred keys: {profile['preferences']['keys']}")
print(f"Preferred moods: {profile['preferences']['moods']}")
```

### Learning Algorithm

The system uses **exponentially-weighted moving averages** to learn preferences:

1. **Initial State**: No preferences (use defaults)
2. **Early Learning**: High learning rate (alpha=0.3)
3. **Established Profile**: Low learning rate (alpha=0.1)

**Preference Categories**:
- **Tempo**: Range and average
- **Key**: Most frequently rated highly
- **Mood**: Emotional preferences
- **Complexity**: Harmonic sophistication level

### Use Cases

- **Personalization**: Tailor to individual users
- **Retention**: Increase satisfaction
- **Discovery**: Suggest based on past likes
- **A/B Testing**: Compare personalized vs. generic

---

## Advanced Analytics

**File**: `app/services/advanced_generator_mixins.py`
**Class**: `AdvancedAnalyticsMixin`

### Purpose

Track comprehensive metrics and provide actionable insights. Monitors:
- Generation statistics
- Quality metrics
- Performance indicators
- User engagement
- System health

### Key Methods

#### `get_analytics_dashboard()`

Get comprehensive analytics dashboard.

**Returns**: Dictionary with analytics data

**Example**:
```python
from app.services.advanced_generator_mixins import AdvancedAnalyticsMixin
from app.services.gospel_generator_refactored import GospelGeneratorService

class AnalyticsGospelGenerator(AdvancedAnalyticsMixin, GospelGeneratorService):
    pass

generator = AnalyticsGospelGenerator()

dashboard = generator.get_analytics_dashboard()

# Overview
print(f"Total generations: {dashboard['overview']['total_generations']}")
print(f"Success rate: {dashboard['overview']['success_rate']*100:.1f}%")
print(f"Avg duration: {dashboard['overview']['average_duration']:.2f}s")

# Distributions
print(f"Most used tempo: {dashboard['distributions']['tempo']['mode']} BPM")
print(f"Top keys: {', '.join(dashboard['distributions']['top_keys'])}")

# Quality metrics
print(f"Avg harmonic complexity: {dashboard['quality_metrics']['avg_harmonic_complexity']:.1f}/10")
print(f"Progression diversity: {dashboard['quality_metrics']['progression_diversity']:.2f}")

# Recent activity
print(f"Last 24h: {dashboard['recent_activity']['last_24h']} generations")

# Health indicators
print(f"Error rate: {dashboard['health_indicators']['error_rate']*100:.1f}%")
print(f"Cache hit rate: {dashboard['health_indicators']['cache_hit_rate']*100:.1f}%")
```

#### `get_quality_report()`

Get quality assessment and recommendations.

**Returns**: Dictionary with quality report

**Example**:
```python
report = generator.get_quality_report()

print(f"Overall quality score: {report['overall_score']:.1f}/10")
print(f"Status: {report['status']}")  # "excellent", "good", "needs_improvement"

print("\nRecommendations:")
for recommendation in report['recommendations']:
    print(f"  • {recommendation}")
```

#### `track_generation(generation_data)`

Record a generation for analytics (called automatically).

**Parameters**:
- `generation_data` (dict): Generation metadata

### Tracked Metrics

**Overview**:
- Total generations
- Success/failure counts
- Average duration
- Total notes generated

**Distributions**:
- Tempo distribution (histogram)
- Key frequency
- Application types
- Bar length patterns

**Quality Metrics**:
- Harmonic complexity (1-10)
- Voice leading score (1-10)
- Progression diversity (0-1)
- Coherence score (1-10)

**Performance**:
- Generation speed
- Cache hit rate
- Error rate
- Response time p50/p95/p99

**User Engagement**:
- Replay rate
- Download rate
- Rating distribution
- Skip rate

### Use Cases

- **Monitoring**: Track system health
- **Optimization**: Identify bottlenecks
- **Quality**: Maintain high standards
- **Reporting**: Generate usage reports
- **A/B Testing**: Compare variants

---

## Usage Examples

### Example 1: Simple Feature Addition

Add ML prediction to gospel generator:

```python
from app.services.advanced_generator_mixins import MLProgressionPredictorMixin
from app.services.gospel_generator_refactored import GospelGeneratorService

class MLGospelGenerator(MLProgressionPredictorMixin, GospelGeneratorService):
    pass

generator = MLGospelGenerator()

# Now has ML prediction capability
predictions = generator.predict_next_chord(["Cmaj7", "Am7"], "user_123")
```

### Example 2: Multiple Features

Combine multiple mixins:

```python
from app.services.advanced_generator_mixins import (
    MLProgressionPredictorMixin,
    UserPreferenceLearningMixin,
    AdvancedAnalyticsMixin
)
from app.services.gospel_generator_refactored import GospelGeneratorService

class EnhancedGospelGenerator(
    MLProgressionPredictorMixin,
    UserPreferenceLearningMixin,
    AdvancedAnalyticsMixin,
    GospelGeneratorService
):
    """Gospel generator with ML, personalization, and analytics"""
    pass

generator = EnhancedGospelGenerator()

# Has all three feature sets
predictions = generator.predict_next_chord(...)
personalized = generator.personalize_request(...)
analytics = generator.get_analytics_dashboard()
```

### Example 3: Production Generator

Full-featured production generator:

```python
from app.services.advanced_generator_mixins import (
    MLProgressionPredictorMixin,
    StreamingGenerationMixin,
    GenreFusionMixin,
    UserPreferenceLearningMixin,
    AdvancedAnalyticsMixin
)
from app.services.base_genre_generator import BaseGenreGenerator
from app.gospel.arranger import GospelArranger

class ProductionGospelGenerator(
    MLProgressionPredictorMixin,           # ML predictions
    StreamingGenerationMixin,              # Real-time streaming
    GenreFusionMixin,                      # Genre blending
    UserPreferenceLearningMixin,           # Personalization
    AdvancedAnalyticsMixin,                # Comprehensive analytics
    BaseGenreGenerator                     # Core functionality
):
    """
    Production-ready gospel generator with all advanced features.
    """

    def __init__(self):
        super().__init__(
            genre_name="Gospel",
            arranger_class=GospelArranger,
            request_schema=GenerateGospelRequest,
            response_schema=GenerateGospelResponse,
            status_schema=GospelGeneratorStatus,
            default_tempo=72,
            output_subdir="gospel_generated"
        )

    def _get_style_context(self) -> str:
        return """Gospel music style context..."""

    def _get_default_progression(self, key: str):
        return ["Imaj7", "vi7", "IVmaj7", "V7"]

    def get_status(self):
        # Enhanced status with analytics
        base_status = super().get_status()
        analytics = self.get_analytics_dashboard()

        return {
            **base_status,
            "analytics_summary": {
                "total_generations": analytics["overview"]["total_generations"],
                "success_rate": analytics["overview"]["success_rate"],
                "cache_hit_rate": analytics["health_indicators"]["cache_hit_rate"]
            }
        }


# Create singleton
production_gospel_generator = ProductionGospelGenerator()
```

---

## Best Practices

### Performance

1. **Selective Features**: Only add mixins you need
2. **Caching**: Use `CachingMixin` for expensive operations
3. **Async**: Use async methods for streaming and predictions
4. **Batch Processing**: Batch analytics updates

### Data Privacy

1. **User Consent**: Get permission before tracking preferences
2. **Anonymization**: Hash user IDs if storing externally
3. **GDPR Compliance**: Provide data export and deletion
4. **Retention**: Set data retention policies

### Quality

1. **Monitoring**: Use `AdvancedAnalyticsMixin` to track quality
2. **A/B Testing**: Compare feature variants
3. **User Feedback**: Collect ratings to improve ML models
4. **Validation**: Test edge cases thoroughly

### Maintainability

1. **Documentation**: Document custom implementations
2. **Testing**: Write tests for custom mixins
3. **Logging**: Use structured logging
4. **Versioning**: Version ML models and preference schemas

---

## Testing

Each mixin has comprehensive unit tests:

```bash
# Run all advanced mixin tests
pytest tests/test_advanced_generator_mixins.py -v

# Run specific mixin tests
pytest tests/test_advanced_generator_mixins.py::TestMLProgressionPredictorMixin -v
pytest tests/test_advanced_generator_mixins.py::TestStreamingGenerationMixin -v
pytest tests/test_advanced_generator_mixins.py::TestGenreFusionMixin -v
pytest tests/test_advanced_generator_mixins.py::TestUserPreferenceLearningMixin -v
pytest tests/test_advanced_generator_mixins.py::TestAdvancedAnalyticsMixin -v
```

---

## Troubleshooting

### ML Predictions Not Improving

**Problem**: Predictions always return same results
**Solution**: Record more user progressions with `record_progression()`

### Streaming Generation Slow

**Problem**: Bars take too long to yield
**Solution**: Optimize `_generate_single_bar()` method, use caching

### Fusion Sounds Unbalanced

**Problem**: One genre overpowers the other
**Solution**: Adjust `primary_weight` parameter (try 0.5 for equal blend)

### Preferences Not Persisting

**Problem**: User preferences reset
**Solution**: Implement persistence layer (database or file storage)

### Analytics Dashboard Empty

**Problem**: No analytics data showing
**Solution**: Ensure `track_generation()` is called after each generation

---

## Migration Guide

### From Basic Generator to Advanced

**Step 1**: Add mixin imports
```python
from app.services.advanced_generator_mixins import MLProgressionPredictorMixin
```

**Step 2**: Add to class inheritance
```python
class MyGenerator(MLProgressionPredictorMixin, BaseGenreGenerator):
    pass
```

**Step 3**: Use new methods
```python
predictions = generator.predict_next_chord(...)
```

**No breaking changes** - existing functionality preserved.

---

## API Reference

See `app/services/advanced_generator_mixins.py` for complete API documentation with type hints and docstrings.

---

## Support

For questions or issues:
1. Check `/examples/advanced_features_demo.py` for working examples
2. Review unit tests in `tests/test_advanced_generator_mixins.py`
3. Consult this guide and inline documentation

---

**Last Updated**: 2025-12-16
**Version**: 1.0
**Authors**: Gospel Keys Development Team
