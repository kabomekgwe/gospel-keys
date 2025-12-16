# Curriculum API - cURL Examples

Base URL: `http://localhost:8000/api/v1`

## RAM Status
**Free RAM: 66MB** (system is under extreme memory pressure - consider closing Chrome/Comet)

---

## 1. Generate Personalized Curriculum (AI-Powered)

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Gospel Piano Journey",
    "duration_weeks": 12,
    "genre": "gospel",
    "skill_level": "intermediate",
    "goals": ["church", "improvise", "byear"]
  }'
```

**Response**: Full curriculum with modules, lessons, and exercises

---

## 2. Create Default Curriculum (Template-Based)

```bash
# List available templates first
curl -X GET "http://localhost:8000/api/v1/curriculum/templates"

# Create from template
curl -X POST "http://localhost:8000/api/v1/curriculum/default" \
  -H "Content-Type: application/json" \
  -d '{
    "template_key": "gospel_essentials"
  }'
```

---

## 3. Get User's Active Curriculum

```bash
curl -X GET "http://localhost:8000/api/v1/curriculum/"
```

---

## 4. List All User Curriculums

```bash
curl -X GET "http://localhost:8000/api/v1/curriculum/list"
```

---

## 5. Get Specific Curriculum by ID

```bash
curl -X GET "http://localhost:8000/api/v1/curriculum/{curriculum_id}"
```

---

## 6. Activate a Curriculum

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/{curriculum_id}/activate"
```

---

## 7. Get Daily Practice Queue

```bash
curl -X GET "http://localhost:8000/api/v1/curriculum/daily"
```

**Response**:
- Exercises due today
- Overdue exercises
- New exercises
- Priority ordering

---

## 8. Submit User Assessment (Update Skill Profile)

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/assessment" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_levels": {
      "technical_ability": 6,
      "theory_knowledge": 5,
      "rhythm_competency": 7,
      "ear_training": 4,
      "improvisation": 5
    },
    "style_familiarity": {
      "gospel": 8,
      "jazz": 5,
      "blues": 4,
      "classical": 3,
      "neo_soul": 6,
      "contemporary": 7
    },
    "primary_goal": "gospel_keys",
    "interests": ["gospel", "jazz", "neo_soul"],
    "weekly_practice_hours": 10.0,
    "learning_velocity": "medium",
    "preferred_style": "visual"
  }'
```

---

## 9. Get User Skill Profile

```bash
curl -X GET "http://localhost:8000/api/v1/curriculum/profile"
```

---

## 10. Complete an Exercise (Update Progress)

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/exercises/{exercise_id}/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "quality": 4,
    "score": 85.5,
    "duration_seconds": 300
  }'
```

**Quality Scale**:
- 0 = Complete blackout
- 1 = Incorrect, recalled with difficulty
- 2 = Correct, recalled with serious difficulty
- 3 = Correct, recalled with hesitation
- 4 = Correct, recalled with ease
- 5 = Perfect response

---

## 11. Get Module Details

```bash
curl -X GET "http://localhost:8000/api/v1/curriculum/modules/{module_id}"
```

---

## 12. Get Lesson Details

```bash
curl -X GET "http://localhost:8000/api/v1/curriculum/lessons/{lesson_id}"
```

---

## 13. Get Lesson Tutorial (AI-Generated)

```bash
# Get tutorial for a lesson
curl -X GET "http://localhost:8000/api/v1/curriculum/lessons/{lesson_id}/tutorial"

# Force regenerate tutorial
curl -X GET "http://localhost:8000/api/v1/curriculum/lessons/{lesson_id}/tutorial?force_regenerate=true"
```

---

## 14. Chat with AI Coach

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/ai-coach/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am struggling with the ii-V-I progression. Can you help?",
    "context": {
      "current_exercise": "Gospel ii-V-I in C",
      "current_lesson": "Module 2: Harmonic Foundation"
    }
  }'
```

**Response**: Personalized coaching based on:
- User skill levels
- Recent performance
- Current curriculum progress
- Specific question/challenge

---

## 15. Get Performance Analysis

```bash
# Last 7 days (default)
curl -X GET "http://localhost:8000/api/v1/curriculum/performance-analysis"

# Custom lookback period
curl -X GET "http://localhost:8000/api/v1/curriculum/performance-analysis?lookback_days=14"
```

**Response includes**:
- Completion rate
- Average quality score
- Struggling exercises
- Mastered exercises
- Weak/strong skill areas
- Recommended actions

---

## 16. Apply Curriculum Adaptations

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/apply-adaptations"
```

**What it does**:
- Analyzes recent performance
- Identifies struggling areas
- Adds remedial exercises
- Adjusts difficulty
- Updates schedule

---

## 17. Generate Diagnostic Assessment

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/generate-diagnostic-assessment"
```

---

## 18. Submit Assessment

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/assessments/{assessment_id}/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "question_1": "answer_1",
      "question_2": "answer_2"
    }
  }'
```

---

## 19. Check Milestone Assessments

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/curricula/{curriculum_id}/check-milestones"
```

**Triggers assessments at**:
- Week 4
- Week 8
- Final (completion)

---

## 20. Add Lick to Practice Queue

```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/add-lick-to-practice" \
  -H "Content-Type: application/json" \
  -d '{
    "lick_name": "Bebop Lick in C",
    "notes": ["C", "D", "E", "F", "G", "A", "Bb", "B"],
    "midi_notes": [60, 62, 64, 65, 67, 69, 70, 71],
    "context": "Cmaj7",
    "style": "bebop",
    "difficulty": "intermediate",
    "duration_beats": 4.0
  }'
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- **200**: Success
- **400**: Bad request (validation error)
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not found
- **500**: Server error

**Error Response Format**:
```json
{
  "detail": "Error message here"
}
```

---

## Notes

1. **Authentication**: Currently using simplified auth (user_id=1). In production, add `Authorization: Bearer <token>` header
2. **IDs**: Replace `{curriculum_id}`, `{exercise_id}`, etc. with actual UUIDs from responses
3. **AI Generation**: `/generate` endpoint may take 5-15 seconds due to local LLM processing
4. **Memory Warning**: Your system has only 66MB free RAM. Close unnecessary apps for better performance.

---

## Quick Test Workflow

```bash
# 1. Generate a curriculum
curl -X POST "http://localhost:8000/api/v1/curriculum/generate" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","duration_weeks":4,"genre":"gospel","skill_level":"beginner","goals":["church"]}'

# 2. Get active curriculum (returns the one you just created)
curl -X GET "http://localhost:8000/api/v1/curriculum/"

# 3. Get daily practice queue
curl -X GET "http://localhost:8000/api/v1/curriculum/daily"

# 4. Complete an exercise
curl -X POST "http://localhost:8000/api/v1/curriculum/exercises/EXERCISE_ID/complete" \
  -H "Content-Type: application/json" \
  -d '{"quality":4,"score":90}'
```
