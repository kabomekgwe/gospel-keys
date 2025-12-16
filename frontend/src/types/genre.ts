/**
 * Genre-specific Type Definitions
 */

export type Genre = 'gospel' | 'jazz' | 'blues' | 'neosoul' | 'classical' | 'reggae' | 'latin' | 'rnb';

export type GospelApplication = 'worship' | 'uptempo' | 'ballad' | 'praise' | 'medley';
export type GospelComplexity = 'simple' | 'moderate' | 'advanced';
export type VoicingStyle = 'traditional' | 'contemporary' | 'jazz_influenced';

export interface GenerateGospelRequest {
  description: string;
  key?: string;
  tempo: number;
  num_bars: number;
  application: GospelApplication;
  ai_percentage?: number; // 0.0-1.0
}

export interface GenerateGospelResponse {
  success: boolean;
  midi_file_base64: string;
  midi_file_path: string;
  chord_progression: string[];
  arrangement_metadata: {
    key: string;
    tempo: number;
    num_bars: number;
    application: string;
    ai_percentage: number;
  };
  notes_preview?: any[];
}

export interface GospelGeneratorStatus {
  mlx_available: boolean;
  mlx_model_trained: boolean;
  gemini_available: boolean;
  recommended_ai_percentage: number;
  dataset_size: number;
  production_ready: boolean;
}

export interface TheoryProgressionRequest {
  base_progression: [string, string][]; // [root, quality]
  key?: string;
  complexity?: GospelComplexity;
  techniques?: ('modal_interchange' | 'chromatic_approach' | 'backdoor' | 'negative_harmony')[];
}

export interface VoicingRequest {
  progression: [string, string][]; // [root, quality]
  voicing_style?: VoicingStyle;
}

export interface GenerateJazzLickRequest {
  context: string; // e.g., "ii-V-I in Bb"
  style?: 'bebop' | 'modal' | 'contemporary';
  difficulty?: number; // 1-10
  bars?: number;
}

export interface JazzLick {
  id?: string;
  name: string;
  notes: string[];
  midi_notes: number[];
  context: string;
  style: string;
  difficulty: number;
  duration_beats: number;
  created_at?: string;
}

export interface GenerateBluesRequest {
  key: string;
  style: 'chicago' | 'delta' | 'jump' | 'shuffle';
  num_bars: number;
  tempo: number;
}

export interface GenerateClassicalRequest {
  style: 'baroque' | 'classical' | 'romantic' | 'impressionist';
  key: string;
  form: 'sonata' | 'prelude' | 'etude' | 'nocturne';
  difficulty: number;
}

export interface GenerateNeosoulRequest {
  key: string;
  tempo: number;
  num_bars: number;
  mood: 'smooth' | 'jazzy' | 'rhythmic';
}

export interface GenerateReggaeRequest {
  key: string;
  tempo: number;
  style: 'roots' | 'dancehall' | 'lovers_rock';
  num_bars: number;
}

export interface GenerateLatinRequest {
  key: string;
  style: 'salsa' | 'bossa_nova' | 'samba' | 'cha_cha';
  tempo: number;
  num_bars: number;
}

export interface GenerateRnBRequest {
  key: string;
  tempo: number;
  era: 'classic' | 'neo' | 'contemporary';
  num_bars: number;
}
