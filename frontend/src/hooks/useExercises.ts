import { useQuery } from '@tanstack/react-query';

/**
 * Exercise API Hooks
 *
 * React Query hooks for exercise management:
 * - Fetching exercises by genre/difficulty
 * - Getting exercise details
 * - Practice session data
 */

const API_BASE = 'http://localhost:8000/api/v1';

export interface Exercise {
  id: string;
  title: string;
  description: string;
  genre: 'gospel' | 'jazz' | 'blues' | 'neosoul' | 'classical';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration: number;
  bpm?: number;
  content: any;
  progress?: number;
  completed?: boolean;
}

// Get exercises by filters
export function useExercises(filters?: {
  genre?: string;
  difficulty?: string;
  limit?: number;
}) {
  const queryParams = new URLSearchParams();
  if (filters?.genre) queryParams.set('genre', filters.genre);
  if (filters?.difficulty) queryParams.set('difficulty', filters.difficulty);
  if (filters?.limit) queryParams.set('limit', filters.limit.toString());

  return useQuery({
    queryKey: ['exercises', filters],
    queryFn: async (): Promise<Exercise[]> => {
      const response = await fetch(
        `${API_BASE}/exercises?${queryParams.toString()}`
      );
      if (!response.ok) {
        throw new Error('Failed to fetch exercises');
      }
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get exercise by ID
export function useExerciseById(exerciseId: string | undefined) {
  return useQuery({
    queryKey: ['exercises', exerciseId],
    queryFn: async (): Promise<Exercise> => {
      const response = await fetch(`${API_BASE}/exercises/${exerciseId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch exercise');
      }
      return response.json();
    },
    enabled: !!exerciseId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Get practice session
export function usePracticeSession() {
  return useQuery({
    queryKey: ['practice', 'session'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/practice/session`);
      if (!response.ok) {
        throw new Error('Failed to fetch practice session');
      }
      return response.json();
    },
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}
