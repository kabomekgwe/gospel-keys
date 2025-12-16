import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

/**
 * Curriculum API Hooks
 *
 * React Query hooks for managing curriculum data:
 * - Fetching curriculum templates
 * - Getting active curriculum
 * - Enrolling in curricula
 * - Tracking progress
 */

const API_BASE = 'http://localhost:8000/api/v1';

// Types based on backend models
export interface Curriculum {
  id: string;
  title: string;
  description: string;
  duration_weeks: number;
  status: 'active' | 'completed' | 'paused';
  progress_percentage: number;
  created_at: string;
  modules?: CurriculumModule[];
}

export interface CurriculumModule {
  id: string;
  title: string;
  description: string;
  theme: string;
  order_index: number;
  start_week: number;
  end_week: number;
  outcomes: string[];
  lessons?: CurriculumLesson[];
}

export interface CurriculumLesson {
  id: string;
  title: string;
  description: string;
  week_number: number;
  theory_content: any;
  concepts: string[];
  estimated_duration_minutes: number;
  exercises?: CurriculumExercise[];
}

export interface CurriculumExercise {
  id: string;
  title: string;
  description: string;
  exercise_type: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimated_duration_minutes: number;
  target_bpm?: number;
  content: any;
}

export interface CurriculumTemplate {
  id: string;
  title: string;
  description: string;
  genre: string;
  skill_level: string;
  duration_weeks: number;
  lessons_count: number;
  is_enrolled: boolean;
}

// Fetch all available curriculum templates
export function useCurriculumTemplates() {
  return useQuery({
    queryKey: ['curriculum', 'templates'],
    queryFn: async (): Promise<CurriculumTemplate[]> => {
      const response = await fetch(`${API_BASE}/curriculum/templates`);
      if (!response.ok) {
        throw new Error('Failed to fetch curriculum templates');
      }
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get user's active curriculum
export function useActiveCurriculum() {
  return useQuery({
    queryKey: ['curriculum', 'active'],
    queryFn: async (): Promise<Curriculum | null> => {
      const response = await fetch(`${API_BASE}/curriculum/`);
      if (response.status === 404) {
        return null; // No active curriculum
      }
      if (!response.ok) {
        throw new Error('Failed to fetch active curriculum');
      }
      return response.json();
    },
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

// Get all user's curricula
export function useUserCurricula() {
  return useQuery({
    queryKey: ['curriculum', 'list'],
    queryFn: async (): Promise<Curriculum[]> => {
      const response = await fetch(`${API_BASE}/curriculum/list`);
      if (!response.ok) {
        throw new Error('Failed to fetch curricula');
      }
      return response.json();
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

// Get curriculum by ID with full details
export function useCurriculumById(curriculumId: string | undefined) {
  return useQuery({
    queryKey: ['curriculum', curriculumId],
    queryFn: async (): Promise<Curriculum> => {
      const response = await fetch(`${API_BASE}/curriculum/${curriculumId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch curriculum details');
      }
      return response.json();
    },
    enabled: !!curriculumId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get daily practice recommendations
export function useDailyPractice() {
  return useQuery({
    queryKey: ['curriculum', 'daily'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/curriculum/daily`);
      if (!response.ok) {
        throw new Error('Failed to fetch daily practice');
      }
      return response.json();
    },
    staleTime: 30 * 1000, // 30 seconds
  });
}

// Enroll in a curriculum
export function useEnrollCurriculum() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (templateId: string) => {
      const response = await fetch(`${API_BASE}/curriculum/enroll/${templateId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error('Failed to enroll in curriculum');
      }
      return response.json();
    },
    onSuccess: () => {
      // Invalidate and refetch curriculum queries
      queryClient.invalidateQueries({ queryKey: ['curriculum'] });
    },
  });
}

// Generate AI curriculum
export function useGenerateCurriculum() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      genre: string;
      skill_level: string;
      focus_areas: string[];
      duration_weeks: number;
    }) => {
      const response = await fetch(`${API_BASE}/curriculum/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        throw new Error('Failed to generate curriculum');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['curriculum'] });
    },
  });
}

// Update curriculum progress
export function useUpdateProgress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (params: {
      curriculumId: string;
      lessonId: string;
      exerciseId: string;
      completed: boolean;
      score?: number;
    }) => {
      const response = await fetch(`${API_BASE}/curriculum/progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });
      if (!response.ok) {
        throw new Error('Failed to update progress');
      }
      return response.json();
    },
    onSuccess: (_, variables) => {
      // Invalidate curriculum and daily practice queries
      queryClient.invalidateQueries({ queryKey: ['curriculum', variables.curriculumId] });
      queryClient.invalidateQueries({ queryKey: ['curriculum', 'daily'] });
      queryClient.invalidateQueries({ queryKey: ['curriculum', 'active'] });
    },
  });
}
