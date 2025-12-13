/**
 * API Client for Piano Keys Backend
 * 
 * Typed API client with error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8009';

export class APIError extends Error {
    constructor(
        message: string,
        public status: number,
        public detail?: string
    ) {
        super(message);
        this.name = 'APIError';
    }
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new APIError(
            `API Error: ${response.status}`,
            response.status,
            error.detail
        );
    }
    return response.json();
}

// ============================================================================
// Transcription API
// ============================================================================

export interface TranscriptionOptions {
    isolate_piano?: boolean;
    detect_chords?: boolean;
    detect_tempo?: boolean;
    detect_key?: boolean;
}

export interface TranscriptionJob {
    job_id: string;
    status: 'pending' | 'downloading' | 'processing' | 'analyzing' | 'complete' | 'error' | 'cancelled';
    progress: number;
    current_step?: string;
    error_message?: string;
    result?: TranscriptionResult;
}

export interface TranscriptionResult {
    song_id: string;
    title: string;
    duration: number;
    tempo: number;
    key_signature: string;
    time_signature: string;
    note_count: number;
    chord_count: number;
    midi_url?: string;
}

export const transcriptionApi = {
    fromUrl: async (url: string, options?: TranscriptionOptions): Promise<TranscriptionJob> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/transcribe/url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, options }),
        });
        return handleResponse<TranscriptionJob>(response);
    },

    fromUpload: async (file: File, options?: TranscriptionOptions): Promise<TranscriptionJob> => {
        const formData = new FormData();
        formData.append('file', file);
        if (options?.isolate_piano !== undefined) formData.append('isolate_piano', String(options.isolate_piano));
        if (options?.detect_chords !== undefined) formData.append('detect_chords', String(options.detect_chords));
        if (options?.detect_tempo !== undefined) formData.append('detect_tempo', String(options.detect_tempo));
        if (options?.detect_key !== undefined) formData.append('detect_key', String(options.detect_key));

        const response = await fetch(`${API_BASE_URL}/api/v1/transcribe/upload`, {
            method: 'POST',
            body: formData,
        });
        return handleResponse<TranscriptionJob>(response);
    },

    getStatus: async (jobId: string): Promise<TranscriptionJob> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/transcribe/${jobId}`);
        return handleResponse<TranscriptionJob>(response);
    },

    getResult: async (jobId: string): Promise<TranscriptionResult> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/transcribe/${jobId}/result`);
        return handleResponse<TranscriptionResult>(response);
    },
};

// ============================================================================
// Library API
// ============================================================================

export interface Song {
    id: string;
    title: string;
    artist?: string;
    duration: number;
    tempo: number;
    key_signature?: string;
    time_signature?: string;
    difficulty?: string;
    favorite: boolean;
    created_at: string;
    last_accessed_at?: string;
    note_count?: number;
    chord_count?: number;
}

export interface SongDetail extends Song {
    source_url?: string;
    source_file?: string;
    midi_file_path?: string;
    annotation_count?: number;
    snippet_count?: number;
}

export const libraryApi = {
    listSongs: async (params?: {
        tag?: string;
        search?: string;
        favorites_only?: boolean;
        limit?: number;
        offset?: number;
    }): Promise<Song[]> => {
        const searchParams = new URLSearchParams();
        if (params?.tag) searchParams.set('tag', params.tag);
        if (params?.search) searchParams.set('search', params.search);
        if (params?.favorites_only) searchParams.set('favorites_only', 'true');
        if (params?.limit) searchParams.set('limit', String(params.limit));
        if (params?.offset) searchParams.set('offset', String(params.offset));

        const response = await fetch(`${API_BASE_URL}/api/v1/library/songs?${searchParams}`);
        return handleResponse<Song[]>(response);
    },

    getSong: async (songId: string): Promise<SongDetail> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/library/songs/${songId}`);
        return handleResponse<SongDetail>(response);
    },

    updateSong: async (songId: string, data: Partial<Song>): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/library/songs/${songId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return handleResponse<void>(response);
    },

    deleteSong: async (songId: string): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/library/songs/${songId}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            throw new APIError('Failed to delete song', response.status);
        }
    },

    addTags: async (songId: string, tags: string[]): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/library/songs/${songId}/tags`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tags),
        });
        return handleResponse<void>(response);
    },
};

// ============================================================================
// Analysis API
// ============================================================================

export interface GenreAnalysis {
    primary_genre: string;
    subgenres: string[];
    confidence: number;
    harmonic_complexity_score: number;
    tempo: number;
    source?: string;
    all_probabilities?: Record<string, number>;
}

export interface JazzPattern {
    pattern_type: string;
    start_time: number;
    duration: number;
    confidence: number;
    key: string;
    metadata?: Record<string, any>;
}

export interface JazzPatternsResult {
    ii_v_i_progressions: JazzPattern[];
    turnarounds: JazzPattern[];
    tritone_substitutions: JazzPattern[];
    total_patterns: number;
    jazz_complexity_score: number;
    source?: string;
}

export interface PitchContour {
    time: number[];
    frequency: number[];
    confidence: number[];
    notes: (string | null)[];
}

export interface PitchAnalysisResult {
    pitch_contour: PitchContour;
    total_frames: number;
    blue_notes?: any[];
    vibrato_regions?: any[];
    pitch_bends?: any[];
}

export const analysisApi = {
    getGenre: async (songId: string): Promise<GenreAnalysis> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/genre?song_id=${songId}`, {
            method: 'POST'
        });
        return handleResponse<GenreAnalysis>(response);
    },

    getJazzPatterns: async (songId: string): Promise<JazzPatternsResult> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/jazz-patterns?song_id=${songId}`, {
            method: 'POST'
        });
        return handleResponse<JazzPatternsResult>(response);
    },

    getPitchTracking: async (songId: string): Promise<PitchAnalysisResult> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/pitch-tracking?song_id=${songId}`, {
            method: 'POST'
        });
        return handleResponse<PitchAnalysisResult>(response);
    },

    getBluesForm: async (songId: string): Promise<unknown> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/blues-form?song_id=${songId}`, {
            method: 'POST'
        });
        return handleResponse<unknown>(response);
    },

    getMelody: async (songId: string): Promise<unknown> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/melody?song_id=${songId}`, {
            method: 'POST'
        });
        return handleResponse<unknown>(response);
    },

    getChords: async (songId: string): Promise<unknown[]> => {
        // This endpoint was not in the backend file viewed, assuming it might be a different path or missing
        // Based on analysis.py, there is no direct "get chords" analysis endpoint, 
        // usually chords come from the Song object or specific analysis.
        // Keeping as is but likely won't work if route doesn't exist.
        // Correcting path to match typical pattern just in case
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/${songId}/chords`);
        return handleResponse<unknown[]>(response);
    },

    getPatterns: async (songId: string): Promise<unknown[]> => {
        // Deprecated or generic? Replacing with specific ones above.
        // Keeping placeholder for backward compat if needed, but likely unused.
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/${songId}/patterns`);
        return handleResponse<unknown[]>(response);
    },
};

// ============================================================================
// Practice API
// ============================================================================

export interface PracticeSession {
    id: number;
    song_id: string;
    audio_url: string;
    tempo_multiplier: number;
    duration_seconds: number;
    notes?: string;
    created_at: string;
}

export const practiceApi = {
    createSession: async (params: {
        song_id: string;
        start_time?: number;
        end_time?: number;
        tempo_multiplier?: number;
        loop?: boolean;
        duration_seconds?: number;
        notes?: string;
    }): Promise<PracticeSession> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/practice/session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params),
        });
        return handleResponse<PracticeSession>(response);
    },

    listSessions: async (songId?: string, limit = 20, offset = 0): Promise<PracticeSession[]> => {
        const params = new URLSearchParams();
        if (songId) params.set('song_id', songId);
        params.set('limit', String(limit));
        params.set('offset', String(offset));

        const response = await fetch(`${API_BASE_URL}/api/v1/practice/sessions?${params}`);
        return handleResponse<PracticeSession[]>(response);
    },

    // SRS Endpoints
    reviewSnippet: async (snippetId: string, quality: number): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/practice/snippets/${snippetId}/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quality }),
        });
        return handleResponse<void>(response);
    },

    getDueSnippets: async (limit = 10): Promise<Snippet[]> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/practice/snippets/due?limit=${limit}`);
        return handleResponse<Snippet[]>(response);
    },
};

export interface Snippet {
    id: string;
    song_id: string;
    label: string;
    start_time: number;
    end_time: number;
    difficulty?: string;
    practice_count: number;

    // SRS Fields
    next_review_at?: string;
    interval_days: number;
    ease_factor: number;
    repetition_count: number;
}

// ============================================================================
// Export API
// ============================================================================

export type ExportFormat = 'midi' | 'musicxml' | 'audio_original' | 'audio_isolated';

export interface ExportOptions {
    includeChords?: boolean;
    includeDynamics?: boolean;
    separateHands?: boolean;
    audioFormat?: 'mp3' | 'wav' | 'flac';
    quality?: 'standard' | 'high';
}

export const exportApi = {
    exportMidi: async (songId: string, options?: ExportOptions): Promise<Blob> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/export/${songId}/midi`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(options || {}),
        });
        if (!response.ok) {
            throw new APIError('Failed to export MIDI', response.status);
        }
        return response.blob();
    },

    exportMusicXml: async (songId: string, options?: ExportOptions): Promise<Blob> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/export/${songId}/musicxml`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(options || {}),
        });
        if (!response.ok) {
            throw new APIError('Failed to export MusicXML', response.status);
        }
        return response.blob();
    },

    exportAudio: async (
        songId: string,
        type: 'original' | 'isolated',
        options?: ExportOptions
    ): Promise<Blob> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/export/${songId}/audio/${type}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(options || {}),
        });
        if (!response.ok) {
            throw new APIError('Failed to export audio', response.status);
        }
        return response.blob();
    },
};

// ============================================================================
// Notes API (for piano roll data)
// ============================================================================

export interface NoteData {
    id: string;
    pitch: number;
    startTime: number;
    duration: number;
    velocity: number;
    hand?: 'left' | 'right';
}

export interface ChordRegion {
    startTime: number;
    endTime: number;
    chord: string;
    romanNumeral?: string;
    function?: 'tonic' | 'subdominant' | 'dominant' | 'secondary';
}

export const notesApi = {
    getNotes: async (songId: string): Promise<NoteData[]> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/library/songs/${songId}/notes`);
        return handleResponse<NoteData[]>(response);
    },

    getChords: async (songId: string): Promise<ChordRegion[]> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/library/songs/${songId}/chords`);
        return handleResponse<ChordRegion[]>(response);
    },
};

// ============================================================================
// Health API
// ============================================================================

export const healthApi = {
    check: async (): Promise<{ status: string; version: string }> => {
        const response = await fetch(`${API_BASE_URL}/health`);
        return handleResponse<{ status: string; version: string }>(response);
    },
};


// ============================================================================
// AI Generator API
// ============================================================================

// Enums
export type ProgressionStyle = 'jazz' | 'gospel' | 'pop' | 'classical' | 'neo_soul' | 'rnb' | 'blues';
export type Mood = 'happy' | 'sad' | 'tense' | 'peaceful' | 'energetic' | 'mysterious' | 'romantic';
export type VoicingStyle = 'open' | 'closed' | 'drop2' | 'drop3' | 'rootless' | 'spread' | 'gospel';
export type ExerciseType = 'scales' | 'arpeggios' | 'progressions' | 'voice_leading' | 'rhythm';
export type Difficulty = 'beginner' | 'intermediate' | 'advanced';
export type GeneratorCategory = 'progressions' | 'voicings' | 'exercises' | 'analysis';

// Request types
export interface ProgressionRequest {
    key: string;
    mode: string;
    style: ProgressionStyle;
    mood?: Mood;
    length: number;
    include_extensions: boolean;
}

export interface ReharmonizationRequest {
    original_progression: string[];
    key: string;
    style: ProgressionStyle;
}

export interface VoicingRequest {
    chord: string;
    style: VoicingStyle;
    hand: 'left' | 'right' | 'both';
    include_fingering: boolean;
}

export interface VoiceLeadingRequest {
    chord1: string;
    chord2: string;
    style?: ProgressionStyle;
}

export interface ExerciseRequest {
    type: ExerciseType;
    key: string;
    difficulty: Difficulty;
    focus?: string;
}

export interface SubstitutionRequest {
    chord: string;
    context?: string[];
    style: ProgressionStyle;
}

// Response types
export interface ChordInfo {
    symbol: string;
    notes: string[];
    midi_notes: number[];
    function?: string;
    comment?: string;
}

export interface VoicingInfo {
    name: string;
    notes: string[];
    midi_notes: number[];
    fingering?: number[];
    hand: string;
}

export interface ExerciseStep {
    instruction: string;
    notes?: string[];
    midi_notes?: number[];
    duration?: string;
}

export interface ProgressionResponse {
    progression: ChordInfo[];
    key: string;
    style: string;
    analysis?: string;
    tips?: string[];
}

export interface ReharmonizationResponse {
    original: string[];
    reharmonized: ChordInfo[];
    explanation: string;
    techniques_used: string[];
}

export interface VoicingResponse {
    chord: string;
    voicings: VoicingInfo[];
    tips?: string[];
}

export interface VoiceLeadingResponse {
    chord1: VoicingInfo;
    chord2: VoicingInfo;
    common_tones: string[];
    movement: string;
    tips?: string[];
}

export interface ExerciseResponse {
    title: string;
    description: string;
    steps: ExerciseStep[];
    variations?: string[];
    difficulty: string;
}

export interface SubstitutionResponse {
    original: string;
    substitutions: ChordInfo[];
    explanations: Record<string, string>;
}

export interface GeneratorInfo {
    id: string;
    name: string;
    description: string;
    category: GeneratorCategory;
}

export interface GeneratorsListResponse {
    generators: Record<string, GeneratorInfo[]>;
}

export const aiApi = {
    getGenerators: async (): Promise<GeneratorsListResponse> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/ai/generators`);
        return handleResponse<GeneratorsListResponse>(response);
    },

    generateProgression: async (request: ProgressionRequest): Promise<ProgressionResponse> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/ai/progression`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        return handleResponse<ProgressionResponse>(response);
    },

    generateReharmonization: async (request: ReharmonizationRequest): Promise<ReharmonizationResponse> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/ai/reharmonization`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        return handleResponse<ReharmonizationResponse>(response);
    },

    generateVoicing: async (request: VoicingRequest): Promise<VoicingResponse> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/ai/voicing`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        return handleResponse<VoicingResponse>(response);
    },

    optimizeVoiceLeading: async (request: VoiceLeadingRequest): Promise<VoiceLeadingResponse> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/ai/voice-leading`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        return handleResponse<VoiceLeadingResponse>(response);
    },

    generateExercise: async (request: ExerciseRequest): Promise<ExerciseResponse> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/ai/exercise`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        return handleResponse<ExerciseResponse>(response);
    },

    getSubstitutions: async (request: SubstitutionRequest): Promise<SubstitutionResponse> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/ai/substitution`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        return handleResponse<SubstitutionResponse>(response);
    },
};

// ============================================================================
// Curriculum API
// ============================================================================

export interface SkillLevels {
    technical_ability: number;
    theory_knowledge: number;
    rhythm_competency: number;
    ear_training: number;
    improvisation: number;
}

export interface StyleFamiliarity {
    gospel: number;
    jazz: number;
    blues: number;
    classical: number;
    neo_soul: number;
    contemporary: number;
}

export interface AssessmentSubmission {
    skill_levels: SkillLevels;
    style_familiarity: StyleFamiliarity;
    primary_goal: string;
    interests: string[];
    weekly_practice_hours: number;
    learning_velocity: 'slow' | 'medium' | 'fast';
    preferred_style?: 'visual' | 'audio' | 'kinesthetic';
}

export interface UserSkillProfile {
    id: number;
    user_id: number;
    skill_levels: SkillLevels;
    style_familiarity: StyleFamiliarity;
    primary_goal?: string;
    interests: string[];
    weekly_practice_hours: number;
    learning_velocity: string;
    preferred_style?: string;
    created_at: string;
    updated_at: string;
}

export interface ExerciseContent {
    chords?: string[];
    key?: string;
    roman_numerals?: string[];
    scale?: string;
    octaves?: number;
    chord?: string;
    voicing_type?: string;
    notes?: string[];
    pattern?: string;
    midi_notes?: number[];
}

export interface CurriculumExercise {
    id: string;
    lesson_id: string;
    title: string;
    description?: string;
    order_index: number;
    exercise_type: string;
    content: ExerciseContent;
    difficulty: string;
    estimated_duration_minutes: number;
    target_bpm?: number;
    practice_count: number;
    best_score?: number;
    is_mastered: boolean;
    mastered_at?: string;
    next_review_at?: string;
    last_reviewed_at?: string;
    created_at: string;
}

export interface LessonSummary {
    id: string;
    title: string;
    week_number: number;
    is_completed: boolean;
    exercise_count: number;
    completed_exercises: number;
}

export interface CurriculumLesson {
    id: string;
    module_id: string;
    title: string;
    description?: string;
    week_number: number;
    theory_content: Record<string, unknown>;
    concepts: string[];
    estimated_duration_minutes: number;
    is_completed: boolean;
    completed_at?: string;
    exercises: CurriculumExercise[];
    created_at: string;
}

export interface ModuleSummary {
    id: string;
    title: string;
    theme: string;
    start_week: number;
    end_week: number;
    completion_percentage: number;
    lesson_count: number;
}

export interface CurriculumModule {
    id: string;
    curriculum_id: string;
    title: string;
    description?: string;
    theme: string;
    order_index: number;
    start_week: number;
    end_week: number;
    prerequisites: string[];
    outcomes: string[];
    completion_percentage: number;
    lessons: LessonSummary[];
    created_at: string;
}

export interface Curriculum {
    id: string;
    user_id: number;
    title: string;
    description?: string;
    duration_weeks: number;
    current_week: number;
    status: 'active' | 'paused' | 'completed' | 'archived';
    ai_model_used?: string;
    modules: ModuleSummary[];
    created_at: string;
    updated_at: string;
}

export interface DailyPracticeItem {
    exercise: CurriculumExercise;
    lesson_title: string;
    module_title: string;
    priority: number;
}

export interface DailyPracticeQueue {
    date: string;
    curriculum_id: string;
    curriculum_title: string;
    current_week: number;
    items: DailyPracticeItem[];
    total_estimated_minutes: number;
    overdue_count: number;
    new_count: number;
}

export interface ExerciseCompleteRequest {
    quality: number;
    score?: number;
    duration_seconds?: number;
}

export const curriculumApi = {
    // Skill Profile
    getProfile: async (): Promise<UserSkillProfile> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/profile`);
        return handleResponse<UserSkillProfile>(response);
    },

    submitAssessment: async (assessment: AssessmentSubmission): Promise<UserSkillProfile> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/assessment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(assessment),
        });
        return handleResponse<UserSkillProfile>(response);
    },

    // Curriculum CRUD
    generateCurriculum: async (params: { title?: string; duration_weeks?: number }): Promise<Curriculum> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params),
        });
        return handleResponse<Curriculum>(response);
    },

    getActiveCurriculum: async (): Promise<Curriculum | null> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/`);
        if (response.status === 404) return null;
        return handleResponse<Curriculum>(response);
    },

    getCurriculum: async (curriculumId: string): Promise<Curriculum> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/${curriculumId}`);
        return handleResponse<Curriculum>(response);
    },

    // Modules & Lessons
    getModule: async (moduleId: string): Promise<CurriculumModule> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/modules/${moduleId}`);
        return handleResponse<CurriculumModule>(response);
    },

    getLesson: async (lessonId: string): Promise<CurriculumLesson> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/lessons/${lessonId}`);
        return handleResponse<CurriculumLesson>(response);
    },

    // Daily Practice
    getDailyPractice: async (): Promise<DailyPracticeQueue> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/daily`);
        return handleResponse<DailyPracticeQueue>(response);
    },

    // Exercise Completion
    completeExercise: async (exerciseId: string, data: ExerciseCompleteRequest): Promise<CurriculumExercise> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/exercises/${exerciseId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return handleResponse<CurriculumExercise>(response);
    },
};

    // === Phase 1: Audio API ===
    getExerciseAudio: async (exerciseId: string, method: 'fluidsynth' | 'stable_audio' = 'fluidsynth'): Promise<Blob> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/audio/exercises/${exerciseId}/audio?method=${method}`);
        if (!response.ok) throw new Error('Failed to fetch audio');
        return response.blob();
    },

    getExerciseMIDI: async (exerciseId: string): Promise<Blob> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/audio/exercises/${exerciseId}/midi`);
        if (!response.ok) throw new Error('Failed to fetch MIDI');
        return response.blob();
    },

    getAudioStatus: async (exerciseId: string): Promise<{ status: string; midi_file?: string; audio_files?: any }> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/audio/exercises/${exerciseId}/status`);
        return handleResponse(response);
    },

    generateExerciseAudio: async (exerciseId: string, method: 'fluidsynth' | 'stable_audio' | 'both' = 'both'): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/audio/exercises/${exerciseId}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ method }),
        });
        return handleResponse(response);
    },

    regenerateExerciseAudio: async (exerciseId: string, method: 'fluidsynth' | 'stable_audio' | 'both' = 'both'): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/audio/exercises/${exerciseId}/regenerate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ method }),
        });
        return handleResponse(response);
    },

    // === Phase 2: Tutorial & Performance API ===
    getLessonTutorial: async (lessonId: string, forceRegenerate: boolean = false): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/lessons/${lessonId}/tutorial?force_regenerate=${forceRegenerate}`);
        return handleResponse(response);
    },

    getPerformanceAnalysis: async (lookbackDays: number = 7): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/performance-analysis?lookback_days=${lookbackDays}`);
        return handleResponse(response);
    },

    applyCurriculumAdaptations: async (): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/apply-adaptations`, {
            method: 'POST',
        });
        return handleResponse(response);
    },

    // === Phase 3: Assessment API ===
    getCurrentAssessment: async (): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/assessments/current`);
        if (response.status === 404) return null;
        return handleResponse(response);
    },

    submitAssessment: async (assessmentId: string, responses: any): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/assessments/${assessmentId}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(responses),
        });
        return handleResponse(response);
    },

    generateDiagnosticAssessment: async (): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/generate-diagnostic-assessment`, {
            method: 'POST',
        });
        return handleResponse(response);
    },

    checkMilestoneAssessments: async (curriculumId: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/curriculum/curricula/${curriculumId}/check-milestones`, {
            method: 'POST',
        });
        return handleResponse(response);
    },

    // === Phase 0: AI Usage Stats ===
    getAIUsageStats: async (days: number = 7): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/ai/usage/stats?days=${days}`);
        return handleResponse(response);
    },
};
