# Gospel Keys Generated Content Integration Guide

## Overview

The Gospel Keys platform now includes comprehensive, automatically-generated educational content:
- **60+ Tutorials** covering music theory and performance techniques
- **147+ Exercises** with progressive difficulty across all genres
- **5 Complete Curriculum Templates** with 46 weeks of structured learning

## Quick Start

### 1. Generate Content

```bash
# From backend directory
python3 app/data/generate_comprehensive_content.py
```

Output:
- `backend/app/data/generated_content/tutorials/tutorials.json`
- `backend/app/data/generated_content/exercises/exercises.json`
- `backend/app/data/generated_content/curriculum/curricula.json`

### 2. Populate Database

```bash
# From backend directory
python populate_default_content.py
```

This creates curriculum templates in the database as "global" resources owned by the admin user.

### 3. Access via Frontend

The generated content is immediately available through the existing API endpoints.

## Frontend Integration

### Load Tutorials

```typescript
// src/hooks/useGeneratedContent.ts
import { useQuery } from '@tanstack/react-query';

export const useTutorials = (genre?: string) => {
  return useQuery({
    queryKey: ['tutorials', genre],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (genre) params.append('genre', genre);

      const response = await fetch(`/api/tutorials?${params}`);
      return response.json();
    }
  });
};
```

### Load Exercises

```typescript
export const useExercises = (filters?: {
  genre?: string;
  type?: string;
  difficulty?: string;
}) => {
  return useQuery({
    queryKey: ['exercises', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.genre) params.append('genre', filters.genre);
      if (filters?.type) params.append('type', filters.type);
      if (filters?.difficulty) params.append('difficulty', filters.difficulty);

      const response = await fetch(`/api/exercises?${params}`);
      return response.json();
    }
  });
};
```

### Create Curriculum from Template

```typescript
export const useCreateCurriculumFromTemplate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (templateKey: string) => {
      const response = await fetch('/api/curriculum/create-from-template', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template_key: templateKey })
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curricula'] });
    }
  });
};
```

### Display Tutorial in Component

```typescript
import { useTutorials } from '@/hooks/useGeneratedContent';

export const TutorialViewer: React.FC<{ genre?: string }> = ({ genre }) => {
  const { data: tutorials, isLoading } = useTutorials(genre);

  if (isLoading) return <div>Loading tutorials...</div>;

  return (
    <div className="space-y-4">
      {tutorials?.map((tutorial) => (
        <div key={tutorial.title} className="border rounded-lg p-4">
          <h3 className="font-bold text-lg">{tutorial.title}</h3>
          <p className="text-sm text-gray-600">{tutorial.description}</p>

          <div className="mt-3 space-y-2">
            <p className="text-xs font-semibold">
              {tutorial.difficulty} • {tutorial.estimated_read_time_minutes} min read
            </p>

            <div className="space-y-2">
              {tutorial.content.sections?.map((section: any, idx: number) => (
                <div key={idx} className="ml-2">
                  <h4 className="font-semibold text-sm">{section.title}</h4>
                  <p className="text-sm">{section.content}</p>
                  {section.key_points && (
                    <ul className="list-disc ml-4 text-xs mt-1">
                      {section.key_points.map((point: string) => (
                        <li key={point}>{point}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>

            {tutorial.examples && (
              <div className="bg-gray-50 p-2 rounded text-xs">
                <p className="font-semibold">Examples:</p>
                <pre>{JSON.stringify(tutorial.examples, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
```

### Display Exercise in Component

```typescript
import { useExercises } from '@/hooks/useGeneratedContent';

export const ExercisePractice: React.FC<{ genre?: string }> = ({ genre }) => {
  const { data: exercises } = useExercises({ genre });
  const [currentExercise, setCurrentExercise] = useState(0);

  if (!exercises?.length) return <div>No exercises found</div>;

  const exercise = exercises[currentExercise];

  return (
    <div className="p-6 border rounded-lg">
      <h2 className="text-xl font-bold">{exercise.title}</h2>
      <p className="text-gray-600 mt-2">{exercise.description}</p>

      <div className="mt-4 space-y-2">
        <p><strong>Type:</strong> {exercise.exercise_type}</p>
        <p><strong>Difficulty:</strong> {exercise.difficulty}</p>
        <p><strong>Duration:</strong> {exercise.estimated_duration_minutes} min</p>
        {exercise.target_bpm && <p><strong>Target BPM:</strong> {exercise.target_bpm}</p>}
      </div>

      {exercise.concepts && (
        <div className="mt-4">
          <p className="font-semibold">Concepts:</p>
          <div className="flex flex-wrap gap-2 mt-2">
            {exercise.concepts.map((concept: string) => (
              <span key={concept} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                {concept}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 flex gap-2">
        <button
          onClick={() => setCurrentExercise((i) => Math.max(0, i - 1))}
          disabled={currentExercise === 0}
        >
          Previous
        </button>
        <span>{currentExercise + 1} / {exercises.length}</span>
        <button
          onClick={() => setCurrentExercise((i) => Math.min(exercises.length - 1, i + 1))}
          disabled={currentExercise === exercises.length - 1}
        >
          Next
        </button>
      </div>
    </div>
  );
};
```

### Curriculum Template Selection

```typescript
import { useCreateCurriculumFromTemplate } from '@/hooks/useGeneratedContent';

export const CurriculumTemplateSelector: React.FC = () => {
  const createMutation = useCreateCurriculumFromTemplate();

  const templates = [
    {
      key: 'gospel_essentials',
      title: 'Gospel Keys Essentials',
      description: 'Master traditional and contemporary gospel piano',
      duration: '12 weeks'
    },
    {
      key: 'jazz_bootcamp',
      title: 'Jazz Improvisation Bootcamp',
      description: 'Learn jazz fundamentals and confident soloing',
      duration: '10 weeks'
    },
    {
      key: 'neosoul_mastery',
      title: 'Neo-Soul Mastery',
      description: 'Sophisticated contemporary R&B and soul sounds',
      duration: '8 weeks'
    },
    {
      key: 'blues_essentials',
      title: 'Blues Piano Essentials',
      description: 'Blues fundamentals and authentic language',
      duration: '6 weeks'
    },
    {
      key: 'classical_theory',
      title: 'Classical Music Theory Foundations',
      description: 'Solid foundation in theory and harmony',
      duration: '10 weeks'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {templates.map((template) => (
        <div key={template.key} className="border rounded-lg p-4 hover:shadow-lg">
          <h3 className="font-bold text-lg">{template.title}</h3>
          <p className="text-gray-600 text-sm mt-2">{template.description}</p>
          <p className="text-xs text-gray-500 mt-2">Duration: {template.duration}</p>

          <button
            onClick={() => createMutation.mutate(template.key)}
            disabled={createMutation.isPending}
            className="mt-4 w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          >
            {createMutation.isPending ? 'Creating...' : 'Start Learning'}
          </button>
        </div>
      ))}
    </div>
  );
};
```

## Backend API Endpoints

### Tutorials

```
GET /api/tutorials
  Query Parameters:
    - genre: gospel | jazz | blues | neosoul | classical
    - difficulty: beginner | intermediate | advanced | expert

  Response: Tutorial[]

GET /api/tutorials/:id
  Response: Tutorial
```

### Exercises

```
GET /api/exercises
  Query Parameters:
    - genre: gospel | jazz | blues | neosoul | classical
    - type: voicing | progression | scale | lick | pattern | rhythm | theory_concept
    - difficulty: beginner | intermediate | advanced

  Response: Exercise[]

GET /api/exercises/:id
  Response: Exercise
```

### Curricula

```
GET /api/curriculum/templates
  Response: CurriculumTemplate[]

POST /api/curriculum/create-from-template
  Body: { template_key: string }
  Response: Curriculum

GET /api/curriculum/:id
  Response: Curriculum (with full structure)
```

## Implementation Steps

### Step 1: Add Backend Routes (Optional - if not already present)

Create `/backend/app/api/routes/generated_content.py`:

```python
from fastapi import APIRouter, Query
from typing import Optional
import json
from pathlib import Path

router = APIRouter(prefix="/api", tags=["generated_content"])

content_dir = Path(__file__).parent.parent.parent / "data" / "generated_content"

@router.get("/tutorials")
async def get_tutorials(
    genre: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None)
):
    """Get tutorials with optional filtering"""
    tutorials_file = content_dir / "tutorials" / "tutorials.json"

    with open(tutorials_file) as f:
        tutorials = json.load(f)

    # Filter by genre
    if genre:
        tutorials = [t for t in tutorials if t['genre'] == genre]

    # Filter by difficulty
    if difficulty:
        tutorials = [t for t in tutorials if t['difficulty'] == difficulty]

    return tutorials

@router.get("/exercises")
async def get_exercises(
    genre: Optional[str] = Query(None),
    exercise_type: Optional[str] = Query(None, alias="type"),
    difficulty: Optional[str] = Query(None)
):
    """Get exercises with optional filtering"""
    exercises_file = content_dir / "exercises" / "exercises.json"

    with open(exercises_file) as f:
        exercises = json.load(f)

    # Apply filters
    if genre:
        exercises = [e for e in exercises if e['genre'] == genre]
    if exercise_type:
        exercises = [e for e in exercises if e['exercise_type'] == exercise_type]
    if difficulty:
        exercises = [e for e in exercises if e['difficulty'] == difficulty]

    return exercises

@router.get("/curriculum/templates")
async def get_curriculum_templates():
    """Get available curriculum templates"""
    curricula_file = content_dir / "curriculum" / "curricula.json"

    with open(curricula_file) as f:
        curricula = json.load(f)

    return curricula
```

### Step 2: Register Routes in main.py

```python
from app.api.routes import generated_content

app.include_router(generated_content.router)
```

### Step 3: Create Frontend Components

Use the component examples provided above in your frontend.

### Step 4: Test Integration

```bash
# Test tutorials endpoint
curl http://localhost:8000/api/tutorials?genre=gospel&difficulty=beginner

# Test exercises endpoint
curl http://localhost:8000/api/exercises?type=voicing&difficulty=intermediate

# Test curricula endpoint
curl http://localhost:8000/api/curriculum/templates
```

## Data Schema Reference

### Tutorial

```typescript
interface Tutorial {
  title: string;
  description: string;
  genre: 'gospel' | 'jazz' | 'blues' | 'neosoul' | 'classical';
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  concepts_covered: string[];
  content: {
    sections: Array<{
      title: string;
      content: string;
      key_points: string[];
    }>;
  };
  examples: Array<{
    [key: string]: any;
  }>;
  practice_exercises: string[];
  estimated_read_time_minutes: number;
}
```

### Exercise

```typescript
interface Exercise {
  title: string;
  description: string;
  exercise_type: 'voicing' | 'progression' | 'scale' | 'lick' | 'pattern' | 'rhythm' | 'theory_concept';
  content: {
    [key: string]: any;
  };
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  genre: 'gospel' | 'jazz' | 'blues' | 'neosoul' | 'classical';
  estimated_duration_minutes: number;
  target_bpm?: number;
  concepts: string[];
  prerequisites: string[];
}
```

### Curriculum

```typescript
interface Curriculum {
  title: string;
  description: string;
  duration_weeks: number;
  target_audience: string;
  learning_outcomes: string[];
  modules_count: number;
}
```

## Performance Considerations

- **Content Size**: ~900KB total (easily fits in memory)
- **Caching**: Content is static - use HTTP caching headers
- **Database**: Exercises and tutorials don't need to be in DB (pure JSON)
- **Curriculum**: Created in DB when users select a template (on-demand cloning)

### Recommended Caching Strategy

```python
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

@router.get("/tutorials")
async def get_tutorials(...):
    tutorials = load_tutorials()

    # Cache for 1 hour
    return JSONResponse(
        content=tutorials,
        headers={
            "Cache-Control": "public, max-age=3600",
            "ETag": f'"{hash(str(tutorials))}"'
        }
    )
```

## Regenerating Content

To update or regenerate content:

```bash
# Regenerate JSON files
python3 backend/app/data/generate_comprehensive_content.py

# Repopulate database (idempotent)
python backend/populate_default_content.py
```

Both scripts are idempotent - safe to run multiple times.

## Future Enhancements

- [ ] MIDI file generation for exercises
- [ ] MusicXML notation generation
- [ ] Audio/video references
- [ ] Interactive ear training integration
- [ ] Personalized exercise sequencing based on student performance
- [ ] Machine-generated variations of exercises
- [ ] Multi-language tutorial support
- [ ] AI-powered exercise recommendations

## Support

For issues with:
- **Content generation**: Check `generate_comprehensive_content.py`
- **Database population**: Check `populate_default_content.py`
- **API integration**: Check generated API routes
- **Frontend rendering**: Check component examples above

## Summary

The generated content system provides:
- ✅ 60+ high-quality tutorials
- ✅ 147+ practice exercises
- ✅ 5 complete curriculum templates
- ✅ 209 unique music concepts
- ✅ Easy frontend integration
- ✅ Idempotent generation and population
- ✅ Immediate API availability
- ✅ Scalable caching strategy

Total content can serve hundreds of users with structured, comprehensive music education.
