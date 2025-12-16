/**
 * TanStack Query hooks for Curriculum API
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, API_ENDPOINTS } from '../lib/api-client';
import type {
  Curriculum,
  CurriculumSummary,
  CurriculumModule,
  CurriculumLesson,
  CurriculumExercise,
  UserSkillProfile,
  AssessmentSubmission,
  DailyPracticeQueue,
  ExerciseCompleteRequest,
  CurriculumTemplate,
  GenerateCurriculumRequest,
  GenerateCurriculumRequest,
  CreateDefaultCurriculumRequest,
  CreateCurriculumFromTemplateRequest,
  AICoachMessage,
  AICoachResponse,
  AddLickToPracticeRequest,
} from '../types/curriculum';

// Query keys
export const curriculumKeys = {
  all: ['curriculum'] as const,
  profile: () => [...curriculumKeys.all, 'profile'] as const,
  active: () => [...curriculumKeys.all, 'active'] as const,
  list: () => [...curriculumKeys.all, 'list'] as const,
  detail: (id: string) => [...curriculumKeys.all, 'detail', id] as const,
  module: (id: string) => [...curriculumKeys.all, 'module', id] as const,
  lesson: (id: string) => [...curriculumKeys.all, 'lesson', id] as const,
  daily: () => [...curriculumKeys.all, 'daily'] as const,
  templates: () => [...curriculumKeys.all, 'templates'] as const,
};

// ============================================================================
// User Skill Profile
// ============================================================================

export function useSkillProfile() {
  return useQuery({
    queryKey: curriculumKeys.profile(),
    queryFn: () => apiClient.get<UserSkillProfile>(API_ENDPOINTS.curriculum.profile),
  });
}

export function useSubmitAssessment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (assessment: AssessmentSubmission) =>
      apiClient.post<UserSkillProfile>(API_ENDPOINTS.curriculum.assessment, assessment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: curriculumKeys.profile() });
    },
  });
}

// ============================================================================
// Curriculum Management
// ============================================================================

export function useActiveCurriculum() {
  return useQuery({
    queryKey: curriculumKeys.active(),
    queryFn: () => apiClient.get<Curriculum | null>(API_ENDPOINTS.curriculum.active),
  });
}

export function useCurriculumList() {
  return useQuery({
    queryKey: curriculumKeys.list(),
    queryFn: () => apiClient.get<CurriculumSummary[]>(API_ENDPOINTS.curriculum.list),
  });
}

export function useCurriculum(id: string) {
  return useQuery({
    queryKey: curriculumKeys.detail(id),
    queryFn: () => apiClient.get<Curriculum>(`${API_ENDPOINTS.curriculum.base}/${id}`),
    enabled: !!id,
  });
}

export function useCurriculumTemplates() {
  return useQuery({
    queryKey: curriculumKeys.templates(),
    queryFn: () => apiClient.get<CurriculumTemplate[]>(API_ENDPOINTS.curriculum.templates),
  });
}

export function useGenerateCurriculum() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: GenerateCurriculumRequest) =>
      apiClient.post<Curriculum>(API_ENDPOINTS.curriculum.generate, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: curriculumKeys.list() });
      queryClient.invalidateQueries({ queryKey: curriculumKeys.active() });
    },
  });
}

export function useCreateDefaultCurriculum() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateDefaultCurriculumRequest) =>
      apiClient.post<Curriculum>(API_ENDPOINTS.curriculum.default, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: curriculumKeys.list() });
    },
  });
}

export function useCreateCurriculumFromTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateCurriculumFromTemplateRequest) =>
      apiClient.post<Curriculum>(API_ENDPOINTS.curriculum.fromTemplate, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: curriculumKeys.list() });
    },
  });
}

export function useActivateCurriculum() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (curriculumId: string) =>
      apiClient.post<Curriculum>(`${API_ENDPOINTS.curriculum.base}/${curriculumId}/activate`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: curriculumKeys.active() });
      queryClient.invalidateQueries({ queryKey: curriculumKeys.list() });
    },
  });
}

// ============================================================================
// Modules & Lessons
// ============================================================================

export function useModule(id: string) {
  return useQuery({
    queryKey: curriculumKeys.module(id),
    queryFn: () => apiClient.get<CurriculumModule>(`${API_ENDPOINTS.curriculum.base}/modules/${id}`),
    enabled: !!id,
  });
}

export function useLesson(id: string) {
  return useQuery({
    queryKey: curriculumKeys.lesson(id),
    queryFn: () => apiClient.get<CurriculumLesson>(`${API_ENDPOINTS.curriculum.base}/lessons/${id}`),
    enabled: !!id,
  });
}

// ============================================================================
// Exercises & Practice
// ============================================================================

export function useCompleteExercise() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ exerciseId, request }: { exerciseId: string; request: ExerciseCompleteRequest }) =>
      apiClient.post<CurriculumExercise>(
        `${API_ENDPOINTS.curriculum.base}/exercises/${exerciseId}/complete`,
        request,
      ),
    onSuccess: (_, { exerciseId }) => {
      // Invalidate all relevant queries
      queryClient.invalidateQueries({ queryKey: curriculumKeys.daily() });
      queryClient.invalidateQueries({ queryKey: curriculumKeys.active() });
      // Could also invalidate specific lesson if we tracked it
    },
  });
}

export function useDailyPractice() {
  return useQuery({
    queryKey: curriculumKeys.daily(),
    queryFn: () => apiClient.get<DailyPracticeQueue>(API_ENDPOINTS.curriculum.daily),
  });
}

export function useAddLickToPractice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: AddLickToPracticeRequest) =>
      apiClient.post<CurriculumExercise>(API_ENDPOINTS.curriculum.addLick, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: curriculumKeys.daily() });
    },
  });
}

// ============================================================================
// AI Coach
// ============================================================================

export function useChatWithAICoach() {
  return useMutation({
    mutationFn: (message: AICoachMessage) =>
      apiClient.post<AICoachResponse>(API_ENDPOINTS.curriculum.aiCoach, message),
  });
}
