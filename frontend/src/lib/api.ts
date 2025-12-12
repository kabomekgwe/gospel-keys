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
    status: 'pending' | 'processing' | 'complete' | 'error';
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
    midi_file: string;
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
    characteristics: Record<string, unknown>;
}

export interface JazzPatterns {
    ii_v_i_patterns: Array<{ start: number; end: number; key: string }>;
    turnarounds: Array<{ start: number; end: number }>;
    tritone_substitutions: Array<{ position: number; original: string; substitution: string }>;
    jazz_complexity_score: number;
}

export const analysisApi = {
    getGenre: async (songId: string): Promise<GenreAnalysis> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/${songId}/genre`);
        return handleResponse<GenreAnalysis>(response);
    },

    getJazzPatterns: async (songId: string): Promise<JazzPatterns> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/${songId}/jazz-patterns`);
        return handleResponse<JazzPatterns>(response);
    },

    getBluesForm: async (songId: string): Promise<unknown> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/${songId}/blues`);
        return handleResponse<unknown>(response);
    },

    getMelody: async (songId: string): Promise<unknown> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/${songId}/melody`);
        return handleResponse<unknown>(response);
    },

    getChords: async (songId: string): Promise<unknown[]> => {
        const response = await fetch(`${API_BASE_URL}/api/v1/analyze/${songId}/chords`);
        return handleResponse<unknown[]>(response);
    },

    getPatterns: async (songId: string): Promise<unknown[]> => {
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
};

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

