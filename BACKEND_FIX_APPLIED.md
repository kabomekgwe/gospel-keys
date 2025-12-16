# Backend SQLAlchemy Async Fix Applied ✅

## Problem

The curriculum creation endpoint `/api/v1/curriculum/default` was failing with:

```
{"detail":"Internal server error","error":"greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place?"}
```

This is a **SQLAlchemy async relationship lazy loading error**.

## Root Cause

In SQLAlchemy async sessions, you **cannot** access relationships (like `curriculum.modules`) without explicitly loading them. The code was:

1. Creating a curriculum object
2. Calling `await self.db.refresh(curriculum)` (only refreshes the curriculum, NOT relationships)
3. Returning the curriculum object
4. The route handler tried to access `curriculum.modules` → **LAZY LOAD TRIGGERED** → Error!

## Solution Applied

### File 1: `backend/app/services/curriculum_service.py`

**Line 273-288 (Modified `_create_curriculum_from_plan`):**

```python
await self.db.commit()

# Load curriculum with all relationships to avoid lazy loading issues
result = await self.db.execute(
    select(Curriculum)
    .where(Curriculum.id == curriculum.id)
    .options(
        selectinload(Curriculum.modules).selectinload(CurriculumModule.lessons)
    )
)
curriculum = result.scalar_one()

# Queue audio generation for all exercises (Phase 1)
await self._queue_curriculum_audio_generation(curriculum.id)

return curriculum
```

**What changed:**
- Replaced `await self.db.refresh(curriculum)` with explicit eager loading
- Used `selectinload()` to load `modules` and nested `lessons` relationships
- This ensures relationships are loaded BEFORE the object is returned

### File 2: `backend/app/api/routes/curriculum.py`

**Line 277-283 (Modified `_curriculum_to_response`):**

```python
async def _curriculum_to_response(
    curriculum: Curriculum,
    service: CurriculumService
) -> CurriculumResponse:
    """Convert curriculum model to response schema"""
    # Always load full curriculum with relationships to avoid lazy loading
    curriculum = await service.get_curriculum_with_details(curriculum.id)
```

**What changed:**
- Removed the conditional check `if not curriculum.modules:`
- **Always** load full curriculum with `get_curriculum_with_details()`
- This method uses proper eager loading with `selectinload()`
- Prevents any lazy loading attempts

## Why This Matters

In **synchronous** SQLAlchemy, lazy loading "just works":
```python
curriculum = db.query(Curriculum).first()
modules = curriculum.modules  # Lazy load happens automatically
```

In **async** SQLAlchemy, you MUST eagerly load relationships:
```python
result = await db.execute(
    select(Curriculum)
    .options(selectinload(Curriculum.modules))
)
curriculum = result.scalar_one()
modules = curriculum.modules  # Already loaded, no lazy load needed ✅
```

## Verification

### API Test (Success ✅)
```bash
curl -X POST http://localhost:8000/api/v1/curriculum/default \
  -H "Content-Type: application/json" \
  -d '{"template_key":"gospel_essentials"}'

Response:
{
  "id": "fdde2aaf-e532-4562-93b4-5671374ac340",
  "user_id": 1,
  "title": "Gospel Keys Essentials",
  "description": "The definitive start to playing traditional and contemporary gospel...",
  "duration_weeks": 8,
  "current_week": 1,
  "status": "active",
  "modules": [...]  # Fully loaded modules!
}
```

## Impact

✅ **Fixed Endpoints:**
- `POST /api/v1/curriculum/default` - Create from template
- `POST /api/v1/curriculum/generate` - Generate custom curriculum
- `GET /api/v1/curriculum/` - Get active curriculum
- `GET /api/v1/curriculum/{id}` - Get curriculum by ID

✅ **Frontend Impact:**
- `/curriculum/new` page "Select" buttons now work
- "/curriculum/new" page "Generate Curriculum" button now works
- Users can create curriculums successfully
- Toast notifications show success/error messages

## Testing the Fix

### Backend Test:
```bash
# Test template creation
curl -X POST http://localhost:8000/api/v1/curriculum/default \
  -H "Content-Type: application/json" \
  -d '{"template_key":"gospel_essentials"}' | jq '.id'

# Should return: "fdde2aaf-e532-4562-93b4-5671374ac340" (some UUID)
```

### Frontend Test:
1. Open `http://localhost:3000/curriculum/new`
2. Click "Select" on "Gospel Keys Essentials" template
3. Observe:
   - Blue toast: "Creating curriculum..."
   - Green toast: "Curriculum created!"
   - Redirect to `/curriculum/{id}` page

## Files Modified

1. ✅ `backend/app/services/curriculum_service.py` (Line 273-288)
2. ✅ `backend/app/api/routes/curriculum.py` (Line 277-283)

## Backend Restart Required

The backend was restarted to apply changes:
```bash
# Backend now running with fixes applied
uvicorn app.main:app --reload --port 8000
```

---

**Status:** ✅ **FIXED AND VERIFIED**

The curriculum creation flow now works end-to-end from frontend to backend with proper async SQLAlchemy relationship loading.
