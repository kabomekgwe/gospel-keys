# Jazz Licks Generator - Enhancement Plan

## Overview

Comprehensive enhancement plan for the jazz licks generator, incorporating musical quality improvements, practice tools, advanced AI features, multiple output formats, deep system integration, and learning tools.

**Available Resources**: Claude Code subscription + Gemini Pro API

## Enhancement Phases

### Phase 1: Quick Wins (Immediate Value)
**Timeline**: Implement first
**Goal**: Improve user experience with high-impact, low-complexity features

#### 1.1 Sheet Music Notation Display
- **Library**: VexFlow (SVG-based music notation)
- **Implementation**:
  - Add VexFlow to frontend dependencies
  - Create `LickNotation.tsx` component
  - Render MIDI notes as standard notation with treble clef
  - Support for swing rhythm marking
- **Files**:
  - `frontend/package.json` (add vexflow)
  - `frontend/src/components/generator/LickNotation.tsx` (new)
  - `frontend/src/components/generator/AIGenerator.tsx` (integrate)

#### 1.2 Variable Playback Speed
- **Feature**: Speed slider (50% - 200%)
- **Implementation**:
  - Modify `playLick()` to accept speed parameter
  - Add speed slider UI control
  - Calculate note spacing based on speed: `200ms / speed`
- **Files**:
  - `frontend/src/components/generator/AIGenerator.tsx`

#### 1.3 Loop Mode
- **Feature**: Continuous lick repetition for practice
- **Implementation**:
  - Add loop toggle button
  - Modify `playLick()` to repeat when loop enabled
  - Add stop button for loop control
- **Files**:
  - `frontend/src/components/generator/AIGenerator.tsx`

#### 1.4 MIDI File Export
- **Library**: `@tonejs/midi` for MIDI file generation
- **Implementation**:
  - Create `exportLickToMIDI()` function
  - Convert lick data to MIDI track
  - Trigger browser download
- **Files**:
  - `frontend/package.json` (add @tonejs/midi)
  - `frontend/src/lib/midi-export.ts` (new)
  - `frontend/src/components/generator/AIGenerator.tsx` (integrate)

**Success Metrics**:
- Sheet music displays correctly for all licks
- Playback speed adjustment works smoothly (50-200%)
- Loop mode enables continuous practice
- MIDI export generates valid .mid files

---

### Phase 2: Core Features (High Impact)
**Timeline**: After Phase 1
**Goal**: Deepen practice capabilities and system integration

#### 2.1 Backing Track Generation
- **Implementation**:
  - Generate simple chord backing using existing chord voicing system
  - Use chord progression from context
  - Sync with lick playback
- **Files**:
  - `frontend/src/lib/backing-track.ts` (new)
  - Leverage existing chord voicing code

#### 2.2 Lick Variations (AI-Powered)
- **Features**:
  - Rhythmic variation (change note durations)
  - Melodic variation (inversion, retrograde, transposition)
  - Harmonic variation (chord substitution)
- **Implementation**:
  - Add `/api/v1/ai/licks/variations` endpoint
  - Gemini prompt for variation generation
  - Validate variations with same pattern library
- **Files**:
  - `backend/app/api/routes/ai.py`
  - `backend/app/services/ai_generator.py`
  - `backend/app/schemas/ai.py`
  - `frontend/src/lib/api.ts`
  - `frontend/src/components/generator/AIGenerator.tsx`

#### 2.3 Curriculum Integration
- **Features**:
  - "Add to Practice Queue" button
  - Auto-tag licks with curriculum metadata
  - SRS (Spaced Repetition System) tracking
- **Implementation**:
  - Create curriculum item from lick
  - Save to user's practice queue
  - Link to existing curriculum system
- **Files**:
  - `backend/app/api/routes/curriculum.py`
  - `frontend/src/components/generator/AIGenerator.tsx`

#### 2.4 Theory Analysis Overlay
- **Features**:
  - Highlight chord tones vs passing tones
  - Show scale degrees for each note
  - Explain approach tones and voice leading
- **Implementation**:
  - Enhance Gemini prompt to include theory analysis
  - Display analysis in collapsible section
- **Files**:
  - `backend/app/services/ai_generator.py`
  - `frontend/src/components/generator/AIGenerator.tsx`

#### 2.5 Progression Alignment
- **Feature**: Auto-suggest licks for chord progressions in transcriptions
- **Implementation**:
  - Add "Suggest Licks" button to transcription chord editor
  - Generate licks matching the current progression
  - Insert into transcription timeline
- **Files**:
  - Integration with transcription system
  - `frontend/src/routes/curriculum/assessment.tsx`

**Success Metrics**:
- Backing tracks play in sync with licks
- Variations maintain musical quality (90%+ validation pass rate)
- Licks successfully save to curriculum queue
- Theory analysis is accurate and educational

---

### Phase 3: Advanced AI (Leverage Claude + Gemini)
**Timeline**: After Phase 2
**Goal**: Cutting-edge AI features using Claude Code subscription

#### 3.1 Style Transfer
- **Feature**: Transform lick from one style to another
- **Example**: "Convert this bebop lick to gospel style"
- **Implementation**:
  - Claude Code agent to analyze lick characteristics
  - Gemini to regenerate in target style
  - Preserve contour while adapting idioms
- **Files**:
  - `backend/app/services/ai_generator.py` (new method)
  - New endpoint: `/api/v1/ai/licks/style-transfer`

#### 3.2 Lick Completion
- **Feature**: Provide partial lick, AI completes it
- **Example**: User plays "C D E" → AI suggests "F G A Bb C"
- **Implementation**:
  - Accept partial MIDI input
  - Gemini continuation with harmonic context
  - Multiple completion options
- **Files**:
  - New endpoint: `/api/v1/ai/licks/complete`
  - Frontend MIDI input component

#### 3.3 Similarity Search
- **Feature**: Find similar licks in database
- **Implementation**:
  - Vector embeddings for lick patterns (interval sequences)
  - Cosine similarity search
  - Store generated licks in vector database
- **Tech**:
  - Cloudflare Vectorize or Pinecone
  - Embed licks as interval + rhythm vectors
- **Files**:
  - `backend/app/services/lick_search.py` (new)
  - Database migration for vector storage

#### 3.4 MIDI Input Feedback
- **Feature**: Play lick on keyboard, get accuracy score
- **Implementation**:
  - Web MIDI API for input capture
  - Compare played notes to target lick
  - Score accuracy: timing, pitch, rhythm
  - Visual feedback (green/red notes)
- **Files**:
  - `frontend/src/lib/midi-input.ts` (new)
  - `frontend/src/components/generator/LickPractice.tsx` (new)

#### 3.5 Historical Context (Claude-Powered)
- **Feature**: Attribute licks to jazz masters, link to recordings
- **Implementation**:
  - Claude analyzes lick characteristics
  - Suggests similar phrases from jazz history
  - Links to YouTube/Spotify timestamps
- **Files**:
  - `backend/app/services/ai_generator.py`
  - Add `historical_context` field to `LicksResponse`

**Success Metrics**:
- Style transfer maintains lick essence (user satisfaction)
- Lick completion sounds musical (90%+ validation pass)
- Similarity search finds relevant results (precision/recall)
- MIDI feedback provides actionable practice guidance

---

### Phase 4: Additional Output Formats
**Timeline**: Parallel with Phase 2/3
**Goal**: Support multiple export and display formats

#### 4.1 MusicXML Export
- **Library**: `music21` (Python) or `opensheetmusicdisplay` (JS)
- **Use Case**: Import into Finale, Sibelius, MuseScore
- **Files**:
  - `backend/app/services/export.py` (new)
  - New endpoint: `/api/v1/ai/licks/export/musicxml`

#### 4.2 PDF Export
- **Implementation**:
  - Render VexFlow notation to canvas
  - Convert to PDF with jsPDF
  - Include lick metadata as text
- **Files**:
  - `frontend/src/lib/pdf-export.ts` (new)

#### 4.3 Audio Synthesis
- **Library**: Tone.js with piano samples
- **Implementation**:
  - Replace basic MIDI playback with realistic piano sound
  - Add reverb, dynamics, swing feel
- **Files**:
  - `frontend/src/lib/audio-engine.ts` (new)
  - `frontend/package.json` (add tone)

#### 4.4 Guitar Tablature
- **Feature**: Display licks as guitar tab (6-string standard tuning)
- **Implementation**:
  - Convert MIDI notes to fret positions
  - Optimize for ergonomic fingering
  - Display tab notation alongside standard notation
- **Library**: Custom tab renderer or AlphaTab
- **Files**:
  - `frontend/src/components/generator/GuitarTab.tsx` (new)

**Success Metrics**:
- MusicXML files import correctly into notation software
- PDF exports are print-ready
- Audio synthesis sounds realistic and musical
- Guitar tab positions are playable and ergonomic

---

### Phase 5: Gospel Generator Integration
**Timeline**: After Phase 2
**Goal**: Bridge licks generator with existing gospel music generation

#### 5.1 Gospel Lick Library
- **Feature**: Specialized gospel lick patterns
- **Implementation**:
  - Expand `_get_gospel_patterns()` with authentic gospel vocabulary
  - Add runs, turnarounds, fills specific to gospel tradition
  - Reference existing gospel chord progressions
- **Files**:
  - `backend/app/jazz/lick_patterns.py`
  - Leverage `backend/app/gospel/patterns/improvisation.py`

#### 5.2 Arrangement Integration
- **Feature**: Auto-insert licks into gospel MIDI arrangements
- **Implementation**:
  - Analyze gospel MIDI arrangement structure
  - Identify insertion points (phrase endings, transitions)
  - Generate contextual licks and insert
- **Files**:
  - `backend/app/gospel/midi_generator.py`
  - Integration with existing gospel pipeline

**Success Metrics**:
- Gospel licks sound authentic (user validation)
- Auto-inserted licks enhance arrangements (A/B testing)

---

## Implementation Priority Matrix

| Feature | Impact | Complexity | Priority |
|---------|--------|------------|----------|
| Sheet Music Display | High | Low | P0 (Phase 1) |
| Playback Speed Control | High | Low | P0 (Phase 1) |
| Loop Mode | High | Low | P0 (Phase 1) |
| MIDI Export | Medium | Low | P0 (Phase 1) |
| Backing Tracks | High | Medium | P1 (Phase 2) |
| Lick Variations | High | Medium | P1 (Phase 2) |
| Theory Analysis | Medium | Low | P1 (Phase 2) |
| Curriculum Integration | High | Medium | P1 (Phase 2) |
| Style Transfer | Medium | High | P2 (Phase 3) |
| MIDI Input Feedback | High | High | P2 (Phase 3) |
| Historical Context | Low | Medium | P3 (Phase 3) |
| Audio Synthesis | Medium | Medium | P2 (Phase 4) |
| PDF Export | Low | Low | P3 (Phase 4) |

## Technology Decisions

### Frontend Libraries
- **VexFlow**: Sheet music rendering (17k stars, active)
- **Tone.js**: Audio synthesis and playback (13k stars)
- **@tonejs/midi**: MIDI file generation (700 stars)
- **Web MIDI API**: Keyboard input (native browser API)

### Backend Libraries
- **music21** (Python): MusicXML export, advanced music analysis
- **mido** (Python): MIDI file manipulation (alternative to @tonejs/midi on backend)

### AI Integration
- **Gemini Pro**: Primary generation engine (creative licks, variations, completions)
- **Claude Code**: Advanced analysis (style transfer, historical context, theory explanations)

### Database
- **Cloudflare Vectorize**: Vector embeddings for similarity search
- **Existing PostgreSQL**: Store generated licks, user favorites, practice history

## Cost Estimates

### AI API Costs (Monthly, 10,000 users)
- **Gemini Pro**: ~$150/month (assuming 0.5M tokens/day)
- **Claude Code**: Subscription already active
- **Total**: ~$150/month incremental

### Infrastructure Costs
- **Cloudflare Vectorize**: ~$20/month (included in Pro plan)
- **Additional Storage**: Minimal (MIDI files ~1KB each)

## Testing Strategy

### Phase 1 Testing
- **Sheet Music**: Verify notation for all 6 styles, all difficulty levels
- **Playback**: Test speeds from 50% to 200%, verify timing accuracy
- **Loop Mode**: Confirm continuous playback, stop functionality
- **MIDI Export**: Validate files open in DAWs (GarageBand, Logic, Ableton)

### Phase 2 Testing
- **Backing Tracks**: Verify chord sync, harmonic accuracy
- **Variations**: Validate 90%+ pass rate on validation rules
- **Curriculum**: Test save/load, SRS tracking, metadata
- **Theory Analysis**: Peer review by music theory experts

### Phase 3 Testing
- **Style Transfer**: A/B test with jazz musicians for authenticity
- **MIDI Feedback**: Accuracy scoring validation with known licks
- **Similarity Search**: Precision/recall metrics, user relevance ratings

## Success Criteria

### User Engagement
- **Target**: 70% of users who generate licks use at least 1 Phase 1 feature
- **Metric**: Track feature usage in analytics

### Musical Quality
- **Target**: 95%+ of generated licks pass validation
- **Metric**: Validation pass rate in logs

### Practice Effectiveness
- **Target**: Users with MIDI feedback show 30% faster improvement
- **Metric**: Assessment scores over time (curriculum integration)

### User Satisfaction
- **Target**: 4.5+ star rating for licks generator
- **Metric**: In-app feedback surveys

## Risk Mitigation

### Technical Risks
- **VexFlow Complexity**: Fallback to simple text notation if rendering fails
- **MIDI API Support**: Progressive enhancement (feature detect, graceful degradation)
- **Vector DB Performance**: Cache common searches, implement pagination

### AI Quality Risks
- **Validation Failures**: Max 3 retries with adjusted prompts
- **Style Transfer Accuracy**: Human review option for critical use cases
- **Gemini Rate Limits**: Queue system, batch processing

## Next Steps

1. **Implement Phase 1** (Quick Wins)
   - Start with sheet music notation (VexFlow integration)
   - Add playback speed + loop mode
   - Implement MIDI export

2. **User Testing** (Phase 1)
   - Deploy to staging
   - Gather user feedback
   - Iterate based on usage data

3. **Plan Phase 2** (Core Features)
   - Detailed technical specs
   - API endpoint design
   - Database schema updates

4. **Parallel Work**
   - Audio synthesis research (Tone.js evaluation)
   - Vector database setup (Cloudflare Vectorize)
   - Gospel integration planning
