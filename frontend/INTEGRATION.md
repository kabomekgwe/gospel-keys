# Frontend-Backend Integration Guide

## Overview

This document describes how the TanStack Start frontend integrates with the FastAPI backend for Gospel Keys.

## Architecture

```
┌─────────────────────┐
│  TanStack Frontend  │
│   (React 19 + TS)   │
└──────────┬──────────┘
           │
           │ HTTP/REST
           │
┌──────────▼──────────┐
│  FastAPI Backend    │
│   (Python 3.13)     │
└─────────────────────┘
```

## API Client Configuration

### Base Configuration

Location: `frontend/src/lib/api-client.ts`

- **Base URL**: `http://localhost:8000` (configurable via `VITE_API_BASE_URL`)
- **API Prefix**: `/api/v1`
- **Error Handling**: Custom `ApiError` class with status codes and response data

### Environment Variables

Create `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## TanStack Query Integration

### Query Configuration

Location: `frontend/src/integrations/tanstack-query/root-provider.tsx`

- **Stale Time**: 60 seconds
- **Cache Time (gcTime)**: 5 minutes
- **Refetch on Focus**: Disabled
- **Retry**: 1 attempt for queries, 0 for mutations

### Custom Hooks

#### Curriculum Hooks (`frontend/src/hooks/useCurriculum.ts`)

| Hook | Type | Purpose |
|------|------|---------|
| `useSkillProfile()` | Query | Get user skill profile |
| `useSubmitAssessment()` | Mutation | Submit assessment |
| `useActiveCurriculum()` | Query | Get active curriculum |
| `useCurriculumList()` | Query | List all curriculums |
| `useCurriculum(id)` | Query | Get curriculum details |
| `useGenerateCurriculum()` | Mutation | Generate new curriculum |
| `useCreateDefaultCurriculum()` | Mutation | Create from template |
| `useActivateCurriculum()` | Mutation | Activate curriculum |
| `useModule(id)` | Query | Get module details |
| `useLesson(id)` | Query | Get lesson details |
| `useCompleteExercise()` | Mutation | Complete exercise |
| `useDailyPractice()` | Query | Get daily practice queue |
| `useAddLickToPractice()` | Mutation | Add lick to practice |
| `useChatWithAICoach()` | Mutation | Chat with AI coach |

#### Genre Hooks (`frontend/src/hooks/useGenre.ts`)

| Hook | Type | Purpose |
|------|------|---------|
| `useGospelStatus()` | Query | Get gospel generator status |
| `useGenerateGospel()` | Mutation | Generate gospel arrangement |
| `useGenerateGospelTheoryProgression()` | Mutation | Generate theory-enhanced progression |
| `useGenerateGospelVoicing()` | Mutation | Generate optimized voicings |
| `useJazzLicks()` | Query | List jazz licks |
| `useGenerateJazzLick()` | Mutation | Generate jazz lick |
| `useGenerateBlues()` | Mutation | Generate blues arrangement |
| `useGenerateNeosoul()` | Mutation | Generate neo-soul arrangement |
| `useGenerateClassical()` | Mutation | Generate classical piece |
| `useGenerateReggae()` | Mutation | Generate reggae arrangement |
| `useGenerateLatin()` | Mutation | Generate Latin arrangement |
| `useGenerateRnB()` | Mutation | Generate R&B arrangement |

## Type Definitions

### Curriculum Types (`frontend/src/types/curriculum.ts`)

- `SkillLevels` - User skill ratings (1-10)
- `StyleFamiliarity` - Genre familiarity ratings
- `UserSkillProfile` - Complete user profile
- `Curriculum` - Curriculum structure
- `CurriculumModule` - Module with lessons
- `CurriculumLesson` - Lesson with exercises
- `CurriculumExercise` - Individual exercise
- `DailyPracticeQueue` - Daily practice items

### Genre Types (`frontend/src/types/genre.ts`)

- `GenerateGospelRequest/Response` - Gospel generation
- `GenerateJazzLickRequest` - Jazz lick generation
- `GenerateBluesRequest` - Blues generation
- And more for each genre...

## Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `index.tsx` | Home page with feature overview |
| `/curriculum` | `curriculum.tsx` | Curriculum layout with navigation |
| `/curriculum/` | `curriculum.index.tsx` | Curriculum list overview |
| `/curriculum/daily` | `curriculum.daily.tsx` | Daily practice queue |
| `/curriculum/new` | `curriculum.new.tsx` | Create new curriculum |
| `/curriculum/$curriculumId` | `curriculum.$curriculumId.tsx` | Curriculum details |
| `/genres` | `genres.tsx` | Genre selection page |
| `/genres/$genreId` | `genres.$genreId.tsx` | Genre-specific generator |

## Running the Application

### Backend (Terminal 1)

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend (Terminal 2)

```bash
cd frontend
pnpm install  # First time only
pnpm dev
```

The frontend will be available at `http://localhost:3000`.

## API Endpoint Mapping

### Curriculum API

| Frontend Hook | Backend Endpoint |
|--------------|------------------|
| `useSkillProfile()` | `GET /api/v1/curriculum/profile` |
| `useSubmitAssessment()` | `POST /api/v1/curriculum/assessment` |
| `useActiveCurriculum()` | `GET /api/v1/curriculum` |
| `useCurriculumList()` | `GET /api/v1/curriculum/list` |
| `useCurriculum(id)` | `GET /api/v1/curriculum/{id}` |
| `useGenerateCurriculum()` | `POST /api/v1/curriculum/generate` |
| `useActivateCurriculum()` | `POST /api/v1/curriculum/{id}/activate` |
| `useDailyPractice()` | `GET /api/v1/curriculum/daily` |
| `useCompleteExercise()` | `POST /api/v1/curriculum/exercises/{id}/complete` |

### Genre API

| Frontend Hook | Backend Endpoint |
|--------------|------------------|
| `useGospelStatus()` | `GET /api/v1/gospel/status` |
| `useGenerateGospel()` | `POST /api/v1/gospel/generate` |
| `useGenerateJazz()` | `POST /api/v1/jazz/generate` |
| `useGenerateBlues()` | `POST /api/v1/blues/generate` |
| (and more for each genre) | |

## Error Handling

### API Client Errors

The `apiClient` automatically handles:
- HTTP error responses (400-599)
- Network errors
- JSON parsing errors

Example error handling in components:

```typescript
const generateCurriculum = useGenerateCurriculum();

const handleGenerate = async () => {
  try {
    const result = await generateCurriculum.mutateAsync({ ... });
    // Success
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`API Error ${error.status}:`, error.data);
    } else {
      console.error('Network error:', error);
    }
  }
};
```

## Cache Invalidation

TanStack Query automatically invalidates and refetches related data after mutations:

```typescript
export function useCompleteExercise() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ exerciseId, request }) => ...,
    onSuccess: () => {
      // Invalidate daily practice queue
      queryClient.invalidateQueries({ queryKey: curriculumKeys.daily() });
      // Invalidate active curriculum
      queryClient.invalidateQueries({ queryKey: curriculumKeys.active() });
    },
  });
}
```

## Development Tips

### Enable DevTools

The app includes TanStack DevTools for debugging:
- **Router DevTools**: Bottom-right corner
- **Query DevTools**: Inspect cache and network requests
- **Store DevTools**: Check global state

### CORS Configuration

Backend CORS is configured in `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Hot Reload

Both backend and frontend support hot reload:
- **Backend**: FastAPI auto-reloads on file changes
- **Frontend**: Vite HMR (Hot Module Replacement)

## Testing Integration

### Manual Testing Checklist

- [ ] Homepage loads and displays active curriculum
- [ ] Can create new curriculum from template
- [ ] Can view curriculum details and modules
- [ ] Daily practice queue loads correctly
- [ ] Can complete exercises and see cache invalidation
- [ ] Genre generators work for all 8 genres
- [ ] Error handling displays user-friendly messages
- [ ] Navigation between routes works smoothly

### API Testing

Use the backend's built-in API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Next Steps

1. **Add Authentication**: Integrate auth hooks and protected routes
2. **WebSocket Support**: Add real-time analysis via WebSocket
3. **File Upload**: Implement MIDI/audio file upload UI
4. **Audio Playback**: Integrate Rust audio engine for playback
5. **Mobile Responsive**: Enhance mobile UI/UX
6. **Offline Support**: Add service worker for offline curriculum access
7. **Performance Monitoring**: Add web-vitals tracking
8. **E2E Testing**: Set up Playwright tests for critical flows

## Troubleshooting

### Backend Not Responding

```bash
# Check if backend is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### CORS Errors

If you see CORS errors in the browser console:
1. Verify backend CORS configuration includes frontend URL
2. Check that backend is running on port 8000
3. Ensure `VITE_API_BASE_URL` is set correctly

### Query Not Updating

If data doesn't update after mutation:
1. Check that `invalidateQueries` is called in `onSuccess`
2. Verify query keys match between hooks
3. Use React Query DevTools to inspect cache

## Resources

- [TanStack Router Docs](https://tanstack.com/router/latest)
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Gospel Keys Backend API Docs](http://localhost:8000/docs)
