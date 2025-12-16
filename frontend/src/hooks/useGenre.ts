/**
 * TanStack Query hooks for Genre-specific Generation APIs
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient, API_ENDPOINTS } from '../lib/api-client';
import type {
  GenerateGospelRequest,
  GenerateGospelResponse,
  GospelGeneratorStatus,
  TheoryProgressionRequest,
  VoicingRequest,
  GenerateJazzLickRequest,
  JazzLick,
  GenerateBluesRequest,
  GenerateClassicalRequest,
  GenerateNeosoulRequest,
  GenerateReggaeRequest,
  GenerateLatinRequest,
  GenerateRnBRequest,
} from '../types/genre';

// Query keys
export const genreKeys = {
  all: ['genre'] as const,
  gospel: {
    status: () => [...genreKeys.all, 'gospel', 'status'] as const,
  },
  jazz: {
    licks: () => [...genreKeys.all, 'jazz', 'licks'] as const,
  },
};

// ============================================================================
// Gospel
// ============================================================================

export function useGospelStatus() {
  return useQuery({
    queryKey: genreKeys.gospel.status(),
    queryFn: () => apiClient.get<GospelGeneratorStatus>(API_ENDPOINTS.gospel.status),
  });
}

export function useGenerateGospel() {
  return useMutation({
    mutationFn: (request: GenerateGospelRequest) =>
      apiClient.post<GenerateGospelResponse>(API_ENDPOINTS.gospel.generate, request),
  });
}

export function useGenerateGospelTheoryProgression() {
  return useMutation({
    mutationFn: (request: TheoryProgressionRequest) =>
      apiClient.post<any>(API_ENDPOINTS.gospel.theory.progression, request),
  });
}

export function useGenerateGospelVoicing() {
  return useMutation({
    mutationFn: (request: VoicingRequest) =>
      apiClient.post<any>(API_ENDPOINTS.gospel.theory.voicing, request),
  });
}

// ============================================================================
// Jazz
// ============================================================================

export function useJazzLicks() {
  return useQuery({
    queryKey: genreKeys.jazz.licks(),
    queryFn: () => apiClient.get<JazzLick[]>(API_ENDPOINTS.jazz.licks),
  });
}

export function useGenerateJazzLick() {
  return useMutation({
    mutationFn: (request: GenerateJazzLickRequest) =>
      apiClient.post<JazzLick>(API_ENDPOINTS.jazz.generateLick, request),
  });
}

export function useGenerateJazz() {
  return useMutation({
    mutationFn: (request: any) =>
      apiClient.post<any>(API_ENDPOINTS.jazz.generate, request),
  });
}

// ============================================================================
// Blues
// ============================================================================

export function useGenerateBlues() {
  return useMutation({
    mutationFn: (request: GenerateBluesRequest) =>
      apiClient.post<any>(API_ENDPOINTS.blues.generate, request),
  });
}

// ============================================================================
// Neo-Soul
// ============================================================================

export function useGenerateNeosoul() {
  return useMutation({
    mutationFn: (request: GenerateNeosoulRequest) =>
      apiClient.post<any>(API_ENDPOINTS.neosoul.generate, request),
  });
}

// ============================================================================
// Classical
// ============================================================================

export function useGenerateClassical() {
  return useMutation({
    mutationFn: (request: GenerateClassicalRequest) =>
      apiClient.post<any>(API_ENDPOINTS.classical.generate, request),
  });
}

// ============================================================================
// Reggae
// ============================================================================

export function useGenerateReggae() {
  return useMutation({
    mutationFn: (request: GenerateReggaeRequest) =>
      apiClient.post<any>(API_ENDPOINTS.reggae.generate, request),
  });
}

// ============================================================================
// Latin
// ============================================================================

export function useGenerateLatin() {
  return useMutation({
    mutationFn: (request: GenerateLatinRequest) =>
      apiClient.post<any>(API_ENDPOINTS.latin.generate, request),
  });
}

// ============================================================================
// R&B
// ============================================================================

export function useGenerateRnB() {
  return useMutation({
    mutationFn: (request: GenerateRnBRequest) =>
      apiClient.post<any>(API_ENDPOINTS.rnb.generate, request),
  });
}
