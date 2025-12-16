/**
 * Curriculum Type Definitions
 * Matches backend schemas
 */

export interface SkillLevels {
  technical_ability: number; // 1-10
  theory_knowledge: number; // 1-10
  rhythm_competency: number; // 1-10
  ear_training: number; // 1-10
  improvisation: number; // 1-10
}

export interface StyleFamiliarity {
  gospel?: number; // 1-10
  jazz?: number;
  blues?: number;
  classical?: number;
  neosoul?: number;
  reggae?: number;
  latin?: number;
  rnb?: number;
}

export interface UserSkillProfile {
  id: string;
  user_id: number;
  skill_levels: SkillLevels;
  style_familiarity: StyleFamiliarity;
  primary_goal: string;
  interests: string[];
  weekly_practice_hours: number;
  learning_velocity: number; // 1-10
  preferred_style: string;
  created_at: string;
  updated_at: string;
}

export interface AssessmentSubmission {
  skill_levels: SkillLevels;
  style_familiarity: StyleFamiliarity;
  primary_goal: string;
  interests: string[];
  weekly_practice_hours: number;
  learning_velocity: number;
  preferred_style: string;
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

export interface CurriculumSummary {
  id: string;
  title: string;
  description: string;
  status: 'draft' | 'active' | 'completed' | 'archived';
  duration_weeks: number;
  current_week: number;
  module_count: number;
  overall_progress: number;
}

export interface Curriculum {
  id: string;
  user_id: number;
  title: string;
  description: string;
  duration_weeks: number;
  current_week: number;
  status: 'draft' | 'active' | 'completed' | 'archived';
  ai_model_used: string;
  modules: ModuleSummary[];
  created_at: string;
  updated_at: string;
}

export interface LessonSummary {
  id: string;
  title: string;
  week_number: number;
  is_completed: boolean;
  exercise_count: number;
  completed_exercises: number;
}

export interface CurriculumModule {
  id: string;
  curriculum_id: string;
  title: string;
  description: string;
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

export interface ExerciseContent {
  instructions?: string;
  notation?: string;
  audio_url?: string;
  midi_url?: string;
  reference_video?: string;
  tips?: string[];
  // Lick-specific fields
  notes?: string[];
  midi_notes?: number[];
  context?: string;
  style?: string;
  duration_beats?: number;
}

export interface CurriculumExercise {
  id: string;
  lesson_id: string;
  title: string;
  description: string;
  order_index: number;
  exercise_type: 'scale' | 'chord' | 'voicing' | 'progression' | 'lick' | 'ear_training' | 'rhythm' | 'technique';
  content: ExerciseContent;
  difficulty: number; // 1-10
  estimated_duration_minutes: number;
  target_bpm?: number;
  practice_count: number;
  best_score?: number;
  is_mastered: boolean;
  mastered_at?: string;
  next_review_at?: string;
  last_reviewed_at?: string;
  interval_days?: number;
  ease_factor?: number;
  repetition_count?: number;
  created_at: string;
}

export interface CurriculumLesson {
  id: string;
  module_id: string;
  title: string;
  description: string;
  week_number: number;
  theory_content: Record<string, any>;
  concepts: string[];
  estimated_duration_minutes: number;
  is_completed: boolean;
  completed_at?: string;
  exercises: CurriculumExercise[];
  created_at: string;
}

export interface DailyPracticeItem {
  exercise: CurriculumExercise;
  lesson_title: string;
  module_title: string;
  priority: number; // 1=overdue, 2=due, 3=new
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
  quality: number; // 1-5 (SRS quality rating)
  score?: number; // Optional performance score
  duration_seconds?: number;
}

export interface CurriculumTemplate {
  id: string;
  type: 'default' | 'dynamic';
  title: string;
  description: string;
  weeks: number;
  key?: string; // Legacy support
}

export interface GenerateCurriculumRequest {
  title: string;
  duration_weeks: number;
  // Wizard data for personalization
  genre?: string;
  skill_level?: string;
  goals?: string[];
  days_per_week?: number;
  session_length?: string;
}

export interface CreateDefaultCurriculumRequest {
  template_key: string;
}

export interface CreateCurriculumFromTemplateRequest {
  template_id: string;
}

export interface AddLickToPracticeRequest {
  lick_name: string;
  notes: string[];
  midi_notes: number[];
  context: string; // e.g., "ii-V-I in Bb"
  style: string; // e.g., "bebop"
  duration_beats: number;
  difficulty: number; // 1-10
}

export interface AICoachMessage {
  text: string;
  context?: {
    current_exercise?: string;
    current_lesson?: string;
  };
}

export interface AICoachResponse {
  response: string;
  context_used: {
    skill_level: number;
    recent_quality: number;
    trend: string;
  };
  timestamp: string;
}
