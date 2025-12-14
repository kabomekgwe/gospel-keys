# Phase 2: Core Features - Detailed Implementation Plan

## Executive Summary

Phase 2 builds on the Phase 1 foundation by adding:
1. **Theory Analysis Overlay** - Educational context for each lick
2. **Backing Track Generation** - Chord accompaniment with rhythm patterns
3. **AI-Powered Lick Variations** - Generate rhythmic, melodic, harmonic variants
4. **Curriculum Integration** - Add licks to SRS practice queue
5. **Progression Alignment** - Suggest licks for detected chord progressions

**Implementation Priority:** Theory Analysis → Backing Tracks → Curriculum Integration → Lick Variations → Progression Alignment

---

## 1. THEORY ANALYSIS OVERLAY

### Overview
Enhance lick generation to include educational theory analysis explaining what makes each lick work.

### Architecture Decision
**Approach:** Enhance existing Gemini prompt, no new endpoints needed.

### Backend Changes

**File:** `/backend/app/services/ai_generator.py`

**Modify `_build_licks_prompt()` method:**

```python
def _build_licks_prompt(self, request: LicksRequest, scales: List[str]) -> str:
    # ... existing prompt building ...

    # ADD: Request theory analysis
    prompt += """

    For EACH lick, also provide theory analysis:
    - chord_tones: Which notes are chord tones vs. passing tones (array of bools)
    - scale_degrees: Scale degree for each note (1-7 with accidentals)
    - approach_tones: Identify chromatic/diatonic approach notes
    - voice_leading: Explain the melodic contour and direction
    - harmonic_function: How the lick outlines the harmony

    Example:
    {
      "name": "Bebop Descending Line",
      "notes": ["C5", "B4", "Bb4", "A4"],
      "midi_notes": [72, 71, 70, 69],
      "theory_analysis": {
        "chord_tones": [true, false, true, false],  // C and Bb are chord tones (Cm7)
        "scale_degrees": ["1", "7", "b7", "6"],
        "approach_tones": ["B4 → chromatic approach to Bb4"],
        "voice_leading": "Stepwise descending motion creates smooth melodic line",
        "harmonic_function": "Outlines minor 7th chord (root, b7) with chromatic passing tone"
      }
    }
    """

    return prompt
```

**Update Schema:** `/backend/app/schemas/ai.py`

```python
class TheoryAnalysis(BaseModel):
    chord_tones: list[bool]  # Which notes are chord tones
    scale_degrees: list[str]  # Scale degree for each note
    approach_tones: list[str]  # Chromatic/diatonic approaches
    voice_leading: str  # Melodic contour explanation
    harmonic_function: str  # How lick outlines harmony

class LickInfo(BaseModel):
    # ... existing fields ...
    theory_analysis: Optional[TheoryAnalysis] = None  # ADD THIS
```

### Frontend Changes

**File:** `/frontend/src/lib/api.ts`

```typescript
export interface TheoryAnalysis {
    chord_tones: boolean[];
    scale_degrees: string[];
    approach_tones: string[];
    voice_leading: string;
    harmonic_function: string;
}

export interface LickInfo {
    // ... existing fields ...
    theory_analysis?: TheoryAnalysis;  // ADD THIS
}
```

**File:** `/frontend/src/components/generator/AIGenerator.tsx`

Add collapsible theory section to each lick card:

```typescript
{lick.theory_analysis && (
    <details className="mt-3 text-xs">
        <summary className="cursor-pointer text-slate-400 hover:text-slate-300">
            📚 Theory Analysis
        </summary>
        <div className="mt-2 p-2 bg-slate-800/50 rounded space-y-1">
            {/* Color-coded notes showing chord tones */}
            <div className="flex gap-1 mb-2">
                {lick.notes.map((note, i) => (
                    <span key={i} className={
                        lick.theory_analysis.chord_tones[i]
                            ? 'bg-emerald-500/20 text-emerald-400'
                            : 'bg-slate-600/20 text-slate-400'
                    } px-2 py-1 rounded text-xs>
                        {note} ({lick.theory_analysis.scale_degrees[i]})
                    </span>
                ))}
            </div>

            <p><strong>Voice Leading:</strong> {lick.theory_analysis.voice_leading}</p>
            <p><strong>Harmonic Function:</strong> {lick.theory_analysis.harmonic_function}</p>

            {lick.theory_analysis.approach_tones.length > 0 && (
                <p><strong>Approach Tones:</strong> {lick.theory_analysis.approach_tones.join(', ')}</p>
            )}
        </div>
    </details>
)}
```

### Implementation Estimate
- **Time:** 2 hours
- **Complexity:** Low
- **Risk:** Low (prompt enhancement only)

---

## 2. BACKING TRACK GENERATION

### Overview
Generate chord accompaniment that plays alongside lick practice, with style-appropriate rhythm patterns.

### Architecture Decision
**Approach:** Frontend-only implementation using existing Tone.js infrastructure.

**Why Frontend-Only:**
- Backing tracks are simple: chord roots + rhythm pattern
- No need for complex gospel arranger (overkill for practice)
- Leverage existing `usePiano` hook
- Real-time generation, no backend latency

### Implementation Design

**File:** `/frontend/src/lib/backing-track.ts` (NEW)

```typescript
import { LickInfo, LickStyle } from './api';

export interface BackingTrackConfig {
    style: LickStyle;
    chords: string[];  // Chord symbols from lick context
    tempo: number;     // BPM
    bars: number;      // Length in bars
}

export interface BackingTrackNote {
    midi: number;
    time: number;   // In seconds
    duration: number; // In seconds
}

/**
 * Generate rhythm pattern based on style
 */
function getRhythmPattern(style: LickStyle): number[] {
    // Returns beat positions (0-4 for 4/4 time)
    switch (style) {
        case 'bebop':
        case 'swing':
            return [0, 2]; // Roots on 1 and 3 (walking bass feel)

        case 'blues':
            return [0, 1, 2, 3]; // Four to the floor

        case 'gospel':
            return [0, 1.5, 2, 3.5]; // Syncopated gospel feel

        case 'bossa':
            return [0, 1.5, 2.5]; // Bossa nova pattern

        case 'modern':
            return [0]; // Whole notes (spacious)

        default:
            return [0, 2]; // Default: half notes
    }
}

/**
 * Generate backing track notes from chord symbols
 */
export function generateBackingTrack(config: BackingTrackConfig): BackingTrackNote[] {
    const { chords, tempo, bars, style } = config;
    const notes: BackingTrackNote[] = [];

    const beatsPerBar = 4;
    const secondsPerBeat = 60 / tempo;
    const barDuration = beatsPerBar * secondsPerBeat;

    const pattern = getRhythmPattern(style);
    const chordDuration = 0.5; // Half second per chord note

    // For each bar
    for (let bar = 0; bar < bars; bar++) {
        const chordIndex = bar % chords.length; // Cycle through chords
        const chord = chords[chordIndex];

        // Get MIDI notes for this chord (root + basic voicing)
        const midiNotes = chordToMidi(chord);

        // Place chord hits according to rhythm pattern
        pattern.forEach(beatPosition => {
            const time = (bar * beatsPerBar + beatPosition) * secondsPerBeat;

            // Add all notes of the chord at this time
            midiNotes.forEach(midi => {
                notes.push({ midi, time, duration: chordDuration });
            });
        });
    }

    return notes;
}

/**
 * Simple chord symbol to MIDI converter
 * Uses root + third + seventh for basic voicing
 */
function chordToMidi(chordSymbol: string): number[] {
    // Parse chord symbol (simplified)
    const root = chordSymbol[0];
    const quality = chordSymbol.slice(1);

    const rootMidi = noteToMidi(root) + 48; // Start at C3

    // Basic voicing: root, third, seventh
    if (quality.includes('maj7')) {
        return [rootMidi, rootMidi + 4, rootMidi + 11]; // Major 7th
    } else if (quality.includes('m7')) {
        return [rootMidi, rootMidi + 3, rootMidi + 10]; // Minor 7th
    } else if (quality.includes('7')) {
        return [rootMidi, rootMidi + 4, rootMidi + 10]; // Dominant 7th
    } else if (quality.includes('m')) {
        return [rootMidi, rootMidi + 3, rootMidi + 7]; // Minor triad
    } else {
        return [rootMidi, rootMidi + 4, rootMidi + 7]; // Major triad
    }
}

function noteToMidi(note: string): number {
    const notes: Record<string, number> = {
        'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
    };
    return notes[note.toUpperCase()] || 0;
}
```

**File:** `/frontend/src/components/generator/AIGenerator.tsx`

Add backing track controls and playback:

```typescript
// State
const [backingTrackEnabled, setBackingTrackEnabled] = useState(false);
const [backingTrackPlaying, setBackingTrackPlaying] = useState(false);

// Import hooks
import { usePiano } from '../../hooks/usePiano';
import { generateBackingTrack } from '../../lib/backing-track';

const { playChord } = usePiano();

// Backing track playback function
const playBackingTrack = (lick: LickInfo) => {
    if (!licksResult) return;

    const track = generateBackingTrack({
        style: licksResult.style as LickStyle,
        chords: licksResult.context.split(' '), // Parse chord symbols
        tempo: 120,
        bars: Math.ceil(lick.duration_beats / 4),
    });

    setBackingTrackPlaying(true);

    // Schedule all backing track notes
    track.forEach(note => {
        setTimeout(() => {
            playChord([note.midi], note.duration, 0.3); // Lower velocity
        }, note.time * 1000);
    });

    // Stop after track ends
    const trackDuration = Math.max(...track.map(n => (n.time + n.duration) * 1000));
    setTimeout(() => setBackingTrackPlaying(false), trackDuration);
};

// Modify playLick to optionally play backing track
const playLickWithBacking = (midiNotes: number[]) => {
    playLick(midiNotes);

    if (backingTrackEnabled && licksResult) {
        // Find which lick is being played
        const lick = licksResult.licks.find(l =>
            JSON.stringify(l.midi_notes) === JSON.stringify(midiNotes)
        );
        if (lick) {
            playBackingTrack(lick);
        }
    }
};

// UI: Add backing track toggle
<div className="flex items-center gap-2">
    <button
        onClick={() => setBackingTrackEnabled(!backingTrackEnabled)}
        className={`flex items-center gap-1 px-3 py-2 rounded text-xs font-medium transition-all ${
            backingTrackEnabled
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'bg-slate-600 text-slate-300 border border-slate-500'
        }`}
    >
        <Music className="w-3 h-3" />
        Backing Track
    </button>
</div>
```

### Implementation Estimate
- **Time:** 4 hours
- **Complexity:** Medium
- **Risk:** Low (uses existing audio infrastructure)

---

## 3. CURRICULUM INTEGRATION

### Overview
Allow users to add generated licks directly to their daily practice queue with automatic SRS scheduling.

### Architecture Decision
**Approach:** Create curriculum exercises from licks, leverage existing SRS system.

### Backend Changes

**File:** `/backend/app/api/routes/curriculum.py`

Add new endpoint:

```python
@router.post("/exercises/from-lick", response_model=CurriculumExercise)
async def create_exercise_from_lick(
    lick_data: dict,
    lesson_id: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """Create a curriculum exercise from a generated lick"""

    # If no lesson_id provided, add to user's active curriculum
    if not lesson_id:
        active_curriculum = await curriculum_service.get_active_curriculum(session)
        if not active_curriculum:
            raise HTTPException(404, "No active curriculum found")

        # Find current week's lesson
        current_lesson = await curriculum_service.get_current_lesson(
            active_curriculum.id, session
        )
        lesson_id = current_lesson.id

    # Create exercise
    exercise = CurriculumExercise(
        id=str(uuid.uuid4()),
        lesson_id=lesson_id,
        exercise_type="lick",
        content_json=json.dumps(lick_data),
        difficulty=lick_data.get('difficulty', 'intermediate'),
        estimated_duration_minutes=5,  # Licks are quick practice items
        next_review_at=datetime.utcnow(),  # Available immediately
        interval_days=1.0,
        ease_factor=2.5,
        repetition_count=0
    )

    session.add(exercise)
    await session.commit()

    # Queue audio generation
    await queue_audio_generation(exercise.id)

    return exercise
```

### Frontend Changes

**File:** `/frontend/src/lib/api.ts`

```typescript
export const curriculumApi = {
    // ... existing methods ...

    addLickToQueue: async (lickData: LickInfo & { style: string; context: string; difficulty: string }) => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/exercises/from-lick`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(lickData),
        });
        return handleResponse<CurriculumExercise>(response);
    },
};
```

**File:** `/frontend/src/components/generator/AIGenerator.tsx`

Add "Add to Practice Queue" button:

```typescript
import { curriculumApi } from '../../lib/api';
import { useMutation } from '@tanstack/react-query';

const addToQueueMutation = useMutation({
    mutationFn: curriculumApi.addLickToQueue,
    onSuccess: () => {
        // Show success toast
        alert('Lick added to your practice queue!');
    },
});

// In lick card UI
<button
    onClick={() => addToQueueMutation.mutate({
        ...lick,
        style: licksResult.style,
        context: licksResult.context,
        difficulty: licksResult.difficulty,
    })}
    className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors"
    disabled={addToQueueMutation.isPending}
>
    <PlusCircle className="w-3 h-3" />
    {addToQueueMutation.isPending ? 'Adding...' : 'Add to Queue'}
</button>
```

### Implementation Estimate
- **Time:** 3 hours
- **Complexity:** Low (leverages existing systems)
- **Risk:** Low

---

## 4. AI-POWERED LICK VARIATIONS

### Overview
Generate rhythmic, melodic, and harmonic variations of existing licks using Gemini Pro.

### Architecture Decision
**Approach:** New backend endpoint with validation, frontend "Generate Variations" UI.

### Backend Changes

**File:** `/backend/app/schemas/ai.py`

```python
class VariationType(str, Enum):
    RHYTHMIC = "rhythmic"      # Change note durations
    MELODIC = "melodic"        # Inversion, transposition, retrograde
    HARMONIC = "harmonic"      # Chord substitution, reharmonization

class LickVariationRequest(BaseModel):
    original_lick: LickInfo
    variation_types: list[VariationType]
    count: int = Field(3, ge=1, le=5)  # Number of variations per type
    context: str  # Original chord context
    style: LickStyle

class LickVariationsResponse(BaseModel):
    original: LickInfo
    variations: dict[str, list[LickInfo]]  # Keyed by variation type
    explanations: dict[str, str]  # What changed in each variation
```

**File:** `/backend/app/services/ai_generator.py`

```python
async def generate_lick_variations(
    self, request: LickVariationRequest
) -> LickVariationsResponse:
    """Generate variations of an existing lick"""

    variations_by_type = {}
    explanations = {}

    for var_type in request.variation_types:
        prompt = self._build_variation_prompt(request, var_type)

        # Generate with retry
        for attempt in range(2):
            response = self.model.generate_content(prompt)
            data = parse_json_from_response(response.text)

            # Validate variations
            valid_variations = []
            for var_data in data.get("variations", []):
                validation = lick_pattern_service.validate_lick(
                    var_data,
                    [request.context],
                    request.style.value,
                    request.original_lick.difficulty
                )
                if validation.is_valid:
                    valid_variations.append(LickInfo(**var_data))

            if len(valid_variations) >= request.count:
                variations_by_type[var_type.value] = valid_variations[:request.count]
                explanations[var_type.value] = data.get("explanation", "")
                break

    return LickVariationsResponse(
        original=request.original_lick,
        variations=variations_by_type,
        explanations=explanations
    )

def _build_variation_prompt(
    self, request: LickVariationRequest, var_type: VariationType
) -> str:
    """Build Gemini prompt for variation generation"""

    original = request.original_lick

    if var_type == VariationType.RHYTHMIC:
        guidelines = """
        Generate RHYTHMIC variations:
        - Keep the same pitches/notes
        - Change note durations (quarter notes → eighths, add syncopation)
        - Maintain same total duration
        - Preserve melodic contour
        """

    elif var_type == VariationType.MELODIC:
        guidelines = """
        Generate MELODIC variations:
        - Inversion: flip intervals upside down
        - Transposition: move up/down by intervals
        - Retrograde: play backwards
        - Ornamentation: add grace notes, turns, trills
        - Keep harmonic function similar
        """

    elif var_type == VariationType.HARMONIC:
        guidelines = """
        Generate HARMONIC variations:
        - Chord substitution: target different chord tones
        - Reharmonization: imply different chords
        - Add chromatic passing tones
        - Alter scale choices
        - Maintain rhythmic structure
        """

    return f"""You are a jazz educator creating lick variations.

Original Lick:
- Name: {original.name}
- Notes: {', '.join(original.notes)}
- MIDI: {original.midi_notes}
- Duration: {original.duration_beats} beats
- Context: {request.context}
- Style: {request.style}

{guidelines}

Generate {request.count} variations following these rules:
- MIDI range: 48-84
- Maintain {request.style} style characteristics
- Keep difficulty level: {original.difficulty}
- Each variation must have a unique name

Return JSON:
{{
  "variations": [
    {{
      "name": "Variation Name",
      "notes": ["C5", "D5", ...],
      "midi_notes": [72, 74, ...],
      "fingering": null,
      "start_note": "C5",
      "end_note": "...",
      "duration_beats": {original.duration_beats},
      "style_tags": ["variation", "{var_type.value}", ...]
    }}
  ],
  "explanation": "Brief explanation of what changed"
}}
"""
```

**File:** `/backend/app/api/routes/ai.py`

```python
@router.post("/licks/variations", response_model=LickVariationsResponse)
async def generate_lick_variations(request: LickVariationRequest):
    try:
        return await ai_generator_service.generate_lick_variations(request)
    except Exception as e:
        raise HTTPException(500, detail=str(e))
```

### Frontend Changes

**File:** `/frontend/src/lib/api.ts`

```typescript
export type VariationType = 'rhythmic' | 'melodic' | 'harmonic';

export interface LickVariationRequest {
    original_lick: LickInfo;
    variation_types: VariationType[];
    count?: number;
    context: string;
    style: LickStyle;
}

export interface LickVariationsResponse {
    original: LickInfo;
    variations: Record<string, LickInfo[]>;
    explanations: Record<string, string>;
}

export const aiApi = {
    // ... existing ...

    generateLickVariations: async (request: LickVariationRequest): Promise<LickVariationsResponse> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/ai/licks/variations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        return handleResponse<LickVariationsResponse>(response);
    },
};
```

**File:** `/frontend/src/components/generator/AIGenerator.tsx`

Add variations UI:

```typescript
const [selectedLickForVariations, setSelectedLickForVariations] = useState<LickInfo | null>(null);
const [variationsResult, setVariationsResult] = useState<LickVariationsResponse | null>(null);

const variationsMutation = useMutation({
    mutationFn: aiApi.generateLickVariations,
    onSuccess: (data) => setVariationsResult(data),
});

// In lick card
<button
    onClick={() => {
        setSelectedLickForVariations(lick);
        variationsMutation.mutate({
            original_lick: lick,
            variation_types: ['rhythmic', 'melodic', 'harmonic'],
            count: 2,
            context: licksResult.context,
            style: licksResult.style as LickStyle,
        });
    }}
    className="..."
>
    <Sparkles className="w-3 h-3" /> Generate Variations
</button>

// Variations modal/panel
{variationsResult && (
    <div className="mt-4 p-4 bg-slate-800 rounded-lg">
        <h4 className="font-semibold mb-3">Variations of "{variationsResult.original.name}"</h4>

        {Object.entries(variationsResult.variations).map(([type, vars]) => (
            <div key={type} className="mb-4">
                <h5 className="text-sm font-medium text-slate-300 mb-2">
                    {type.charAt(0).toUpperCase() + type.slice(1)} Variations
                </h5>
                <p className="text-xs text-slate-400 mb-2">
                    {variationsResult.explanations[type]}
                </p>

                <div className="grid grid-cols-2 gap-2">
                    {vars.map((variant, i) => (
                        <div key={i} className="p-2 bg-slate-700/50 rounded">
                            <div className="text-xs font-medium">{variant.name}</div>
                            <div className="text-xs text-slate-400">{variant.notes.join(' → ')}</div>
                            <button onClick={() => playLick(variant.midi_notes)}>
                                <Volume2 className="w-3 h-3" /> Play
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        ))}
    </div>
)}
```

### Implementation Estimate
- **Time:** 6 hours
- **Complexity:** Medium-High
- **Risk:** Medium (depends on AI quality)

---

## 5. PROGRESSION ALIGNMENT

### Overview
Suggest licks for detected chord progressions in transcriptions and gospel generation.

### Architecture Decision
**Approach:** Integrate with existing progression detection and transcription UI.

### Implementation Points

**A. Transcription Analysis Integration**

**File:** `/frontend/src/components/analysis/ProgressionPatternDisplay.tsx`

Add "Suggest Licks" button:

```typescript
const suggestLicksMutation = useMutation({
    mutationFn: ({ pattern, difficulty }: { pattern: string; difficulty: Difficulty }) =>
        aiApi.generateLicks({
            style: 'jazz',  // Infer from pattern type
            context_type: 'progression',
            context: pattern,
            difficulty,
            length_bars: 2,
            include_chromatics: true,
        }),
});

// In pattern display UI
{pattern && (
    <button
        onClick={() => suggestLicksMutation.mutate({
            pattern: pattern.progression_string,
            difficulty: 'intermediate',
        })}
        className="..."
    >
        <Zap /> Suggest Licks for This Progression
    </button>
)}

{suggestLicksMutation.data && (
    <LicksDisplay licks={suggestLicksMutation.data.licks} />
)}
```

**B. Gospel Generation Integration**

**File:** `/backend/app/gospel/arrangement/arranger.py`

Add lick insertion option:

```python
def arrange_with_licks(
    self,
    chord_progression: List[str],
    application_type: str = "worship",
    insert_licks: bool = False,
    lick_probability: float = 0.3
) -> Arrangement:
    """Generate arrangement with optional lick insertion"""

    # ... existing arrangement logic ...

    if insert_licks:
        for bar_idx, chord in enumerate(chord_progression):
            if random.random() < lick_probability:
                # Generate contextual lick
                lick = self._generate_contextual_lick(
                    chord, bar_idx, chord_progression
                )
                # Insert into right hand at phrase ending
                if bar_idx % 4 == 3:  # End of 4-bar phrase
                    self._insert_lick_notes(arrangement, lick, bar_idx)

    return arrangement
```

### Implementation Estimate
- **Time:** 5 hours
- **Complexity:** Medium
- **Risk:** Low (integrates existing systems)

---

## IMPLEMENTATION ORDER & TIMELINE

### Week 1: Foundation (Theory + Backing)
- **Day 1-2:** Theory analysis overlay (2 hours)
- **Day 3-4:** Backing track generation (4 hours)
- **Day 5:** Testing and refinement

### Week 2: Integration (Curriculum + Variations)
- **Day 1-2:** Curriculum integration (3 hours)
- **Day 3-5:** Lick variations system (6 hours)

### Week 3: Advanced (Progression Alignment)
- **Day 1-3:** Progression alignment (5 hours)
- **Day 4-5:** End-to-end testing, documentation

**Total Estimated Time:** 20 hours over 3 weeks

---

## SUCCESS METRICS

### Quantitative
- **Theory Analysis:** 100% of licks include theory breakdown
- **Backing Tracks:** Sync accuracy within 50ms
- **Curriculum:** 70%+ of generated licks successfully added to queue
- **Variations:** 80%+ variation pass rate on first generation
- **Progression:** 90%+ relevant lick suggestions

### Qualitative
- Users understand WHY licks work (theory helps learning)
- Practice feels more musical (backing tracks)
- Licks integrated into daily routine (curriculum)
- Creative exploration enabled (variations)
- Contextual suggestions are helpful (progression alignment)

---

## RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| AI theory analysis inaccurate | Medium | Medium | Validate with music theory rules |
| Backing track timing drift | Low | Medium | Use Tone.js Transport for sync |
| Curriculum system breaking changes | Low | High | Comprehensive testing, rollback plan |
| Variation quality poor | Medium | Medium | Validation retry logic, human review |
| Progression detection missing patterns | Low | Low | Graceful fallback, manual entry option |

---

## DEPENDENCIES

### Required Before Implementation
- ✅ Phase 1 complete (playback, MIDI, notation)
- ✅ Lick generation API functional
- ✅ Curriculum system stable
- ✅ Audio infrastructure (Tone.js)

### External Dependencies
- Gemini Pro API availability
- Tone.js library stability
- VexFlow for notation (already installed)

---

## TECHNICAL DEBT & FUTURE WORK

### Identified Tech Debt
- Pre-existing api.ts syntax error (unrelated to licks)
- MIDI export could use more sophisticated duration calculation
- Backing tracks currently use simple voicings (could leverage gospel arranger)

### Future Enhancements (Phase 3+)
- Style transfer between lick styles
- MIDI input feedback
- Similarity search with vector DB
- Historical context (jazz masters attribution)
