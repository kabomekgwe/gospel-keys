# Gospel Keys API Testing Guide

## System Status

**⚠️ RAM Warning**: Your system has only **66MB free RAM** out of 24GB total.
**Memory Pressure**: EXTREME (23GB compressed)

### Memory Hogs:
- Google Chrome: ~3-4GB (20+ processes)
- Antigravity/VS Code: ~3GB
- Comet: ~1GB

**Recommendation**: Close Chrome or Comet to free up 3-5GB before running API tests.

---

## Quick Start

### 1. Backend is Already Running

Your FastAPI backend is running on:
```
http://localhost:8000
```

Processes:
- PID 68088: uvicorn (main)
- PID 68098: uvicorn worker

### 2. Frontend is Running

Your React frontend is running on:
```
http://localhost:3000
```

---

## Testing Options

### Option A: Use cURL (Terminal)

All examples are in `CURRICULUM_API_EXAMPLES.md`:

```bash
# Quick test - Generate a curriculum
curl -X POST "http://localhost:8000/api/v1/curriculum/generate" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Curriculum","duration_weeks":4,"genre":"gospel","skill_level":"beginner","goals":["church"]}'
```

### Option B: Use Postman

1. **Import the Collection**:
   - Open Postman
   - Click "Import"
   - Select `Gospel_Keys_Curriculum_API.postman_collection.json`

2. **Set Base URL** (already configured):
   - Variable: `baseUrl`
   - Value: `http://localhost:8000/api/v1`

3. **Start Testing**:
   - Expand folder "1. Curriculum Generation"
   - Click "Generate Personalized Curriculum (AI)"
   - Click "Send"

4. **Save IDs for Later Requests**:
   - Copy `curriculum_id` from response
   - Set it in Postman variables (`curriculum_id`)

### Option C: Use HTTPie (Cleaner than cURL)

Install:
```bash
brew install httpie
```

Test:
```bash
http POST localhost:8000/api/v1/curriculum/generate \
  title="Test" \
  duration_weeks:=4 \
  genre="gospel" \
  skill_level="beginner" \
  goals:='["church"]'
```

### Option D: Use Your Frontend

Visit `http://localhost:3000` and use the UI to trigger API calls.

---

## API Documentation

### Interactive Docs (Swagger UI)

Visit: `http://localhost:8000/docs`

This provides:
- All endpoints listed
- Request/response schemas
- "Try it out" interactive testing
- Auto-generated examples

### Alternative Docs (ReDoc)

Visit: `http://localhost:8000/redoc`

Cleaner, more readable format.

---

## Testing Workflow

### 1. Generate a Curriculum

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Gospel Foundations",
    "duration_weeks": 8,
    "genre": "gospel",
    "skill_level": "intermediate",
    "goals": ["church", "improvise"]
  }'
```

**Expected Response** (takes 5-15 seconds):
```json
{
  "id": "uuid-here",
  "user_id": 1,
  "title": "Gospel Foundations",
  "description": "AI-generated description...",
  "duration_weeks": 8,
  "current_week": 1,
  "status": "active",
  "ai_model_used": "gemini-flash",
  "modules": [
    {
      "id": "module-uuid",
      "title": "Module 1: Foundation",
      "theme": "basics",
      "start_week": 1,
      "end_week": 2,
      "lesson_count": 4
    }
  ],
  "created_at": "2025-01-16T...",
  "updated_at": "2025-01-16T..."
}
```

**Save the `id` field** - you'll need it for subsequent requests.

---

### 2. Get Daily Practice Queue

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/curriculum/daily"
```

**Response**:
```json
{
  "date": "2025-01-16T...",
  "curriculum_id": "uuid",
  "curriculum_title": "Gospel Foundations",
  "current_week": 1,
  "items": [
    {
      "exercise": {
        "id": "exercise-uuid",
        "title": "C Major Scale",
        "exercise_type": "scale",
        "difficulty": "beginner",
        "estimated_duration_minutes": 10
      },
      "lesson_title": "Lesson 1: Scales",
      "module_title": "Module 1: Foundation",
      "priority": 3
    }
  ],
  "total_estimated_minutes": 30,
  "overdue_count": 0,
  "new_count": 5
}
```

---

### 3. Complete an Exercise

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/exercises/EXERCISE_ID/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "quality": 4,
    "score": 87.5,
    "duration_seconds": 180
  }'
```

**Quality Scale**:
- **0**: Complete blackout (forgot everything)
- **1**: Incorrect, recalled with difficulty
- **2**: Correct, but with serious difficulty
- **3**: Correct, recalled with hesitation
- **4**: Correct, recalled with ease
- **5**: Perfect response

**Response**:
```json
{
  "id": "exercise-uuid",
  "title": "C Major Scale",
  "practice_count": 1,
  "best_score": 87.5,
  "is_mastered": false,
  "next_review_at": "2025-01-17T...",
  "interval_days": 1.0,
  "ease_factor": 2.5
}
```

---

### 4. Chat with AI Coach

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/curriculum/ai-coach/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I keep messing up the ii-V-I progression. What should I focus on?",
    "context": {
      "current_exercise": "Gospel ii-V-I in C",
      "current_lesson": "Module 2: Harmonic Progressions"
    }
  }'
```

**Response**:
```json
{
  "response": "I can see you're working on the ii-V-I progression in C! This is such a foundational pattern in gospel music...",
  "context_used": {
    "skill_level": 6,
    "recent_quality": 3.8,
    "trend": "improving"
  },
  "timestamp": "2025-01-16T..."
}
```

---

## Environment Variables

Check your `.env` file for:

```bash
# Required for AI features
GEMINI_API_KEY=your_key_here

# Database (already configured)
DATABASE_URL=postgresql://...

# Optional: Multi-model LLM
ENABLE_LOCAL_LLM=true
```

---

## Troubleshooting

### 1. "AI curriculum generation is unavailable"

**Cause**: Missing or invalid `GEMINI_API_KEY`

**Fix**:
```bash
# Check if key is set
echo $GEMINI_API_KEY

# Add to .env file
echo 'GEMINI_API_KEY=your_key_here' >> backend/.env

# Restart backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

---

### 2. "Memory Error" or System Freezing

**Cause**: System has only 66MB free RAM

**Fix**:
```bash
# Close Chrome (frees 3-4GB)
killall "Google Chrome"

# Or close Comet (frees 1GB)
killall "Comet"
```

---

### 3. "Qwen2.5-14B requires ~12GB RAM"

This warning appears when trying to load the 14B model on low RAM.

**Fix**: The system automatically falls back to smaller models (Phi-3.5 Mini). No action needed.

---

### 4. CORS Errors in Browser

**Fix**: Already handled in backend. If issues persist:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Notes

### AI Generation Times

| Endpoint | Model | Expected Time |
|----------|-------|---------------|
| `/generate` (curriculum) | Gemini Flash | 5-15 seconds |
| `/ai-coach/chat` | Gemini Pro | 2-5 seconds |
| `/lessons/{id}/tutorial` | Gemini Flash | 3-8 seconds |
| `/assessment/evaluate` | Local LLM | 1-3 seconds |

### Rate Limits

**Local LLMs**: No rate limits
**Gemini API**: 60 requests/minute (Free tier)

---

## Next Steps

1. **Close memory-hungry apps** (Chrome recommended)
2. **Import Postman collection** for easy testing
3. **Generate a test curriculum** using `/curriculum/generate`
4. **Try the daily practice flow**:
   - Get daily queue → Complete exercise → Check progress
5. **Test AI coach** with questions about your practice

---

## Files Created

- ✅ `CURRICULUM_API_EXAMPLES.md` - All cURL examples
- ✅ `Gospel_Keys_Curriculum_API.postman_collection.json` - Postman collection
- ✅ `API_TESTING_GUIDE.md` - This file

---

## Support

If you encounter issues:

1. Check backend logs: Terminal running `uvicorn`
2. Check browser console: Press F12
3. Verify database is running: `psql -U postgres -l`
4. Check environment variables: `cat backend/.env`
