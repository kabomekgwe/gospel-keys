/**
 * API Client Configuration
 * Base client for Gospel Keys backend API
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_V1_PREFIX = '/api/v1';

export const API_ENDPOINTS = {
  // Health & Status
  health: '/health',
  root: '/',

  // Authentication
  auth: {
    login: `${API_V1_PREFIX}/auth/login`,
    register: `${API_V1_PREFIX}/auth/register`,
    logout: `${API_V1_PREFIX}/auth/logout`,
    me: `${API_V1_PREFIX}/auth/me`,
  },

  // Curriculum
  curriculum: {
    base: `${API_V1_PREFIX}/curriculum`,
    profile: `${API_V1_PREFIX}/curriculum/profile`,
    assessment: `${API_V1_PREFIX}/curriculum/assessment`,
    generate: `${API_V1_PREFIX}/curriculum/generate`,
    default: `${API_V1_PREFIX}/curriculum/default`,
    templates: `${API_V1_PREFIX}/curriculum/templates`,
    list: `${API_V1_PREFIX}/curriculum/list`,
    active: `${API_V1_PREFIX}/curriculum`,
    daily: `${API_V1_PREFIX}/curriculum/daily`,
    aiCoach: `${API_V1_PREFIX}/curriculum/ai-coach/chat`,
    addLick: `${API_V1_PREFIX}/curriculum/add-lick-to-practice`,
  },

  // Genre-specific endpoints
  gospel: {
    generate: `${API_V1_PREFIX}/gospel/generate`,
    status: `${API_V1_PREFIX}/gospel/status`,
    theory: {
      progression: `${API_V1_PREFIX}/gospel/theory/progression`,
      voicing: `${API_V1_PREFIX}/gospel/theory/voicing`,
    },
  },

  jazz: {
    generate: `${API_V1_PREFIX}/jazz/generate`,
    licks: `${API_V1_PREFIX}/jazz/licks`,
    generateLick: `${API_V1_PREFIX}/jazz/generate-lick`,
  },

  blues: {
    generate: `${API_V1_PREFIX}/blues/generate`,
  },

  neosoul: {
    generate: `${API_V1_PREFIX}/neosoul/generate`,
  },

  classical: {
    generate: `${API_V1_PREFIX}/classical/generate`,
  },

  reggae: {
    generate: `${API_V1_PREFIX}/reggae/generate`,
  },

  latin: {
    generate: `${API_V1_PREFIX}/latin/generate`,
  },

  rnb: {
    generate: `${API_V1_PREFIX}/rnb/generate`,
  },

  // Theory & Tools
  theory: {
    analyze: `${API_V1_PREFIX}/theory/analyze`,
    suggestions: `${API_V1_PREFIX}/theory/suggestions`,
  },

  theoryTools: {
    chordAnalysis: `${API_V1_PREFIX}/theory-tools/chord-analysis`,
    scaleExplorer: `${API_V1_PREFIX}/theory-tools/scale-explorer`,
    voicingGenerator: `${API_V1_PREFIX}/theory-tools/voicing-generator`,
    progressionBuilder: `${API_V1_PREFIX}/theory-tools/progression-builder`,
  },

  // Practice & Analysis
  practice: {
    sessions: `${API_V1_PREFIX}/practice/sessions`,
    submit: `${API_V1_PREFIX}/practice/submit`,
  },

  analysis: {
    performance: `${API_V1_PREFIX}/analysis/performance`,
    realtime: `${API_V1_PREFIX}/realtime-analysis`,
  },

  // Library & Collections
  library: {
    list: `${API_V1_PREFIX}/library`,
    save: `${API_V1_PREFIX}/library/save`,
  },

  collections: {
    list: `${API_V1_PREFIX}/collections`,
    create: `${API_V1_PREFIX}/collections/create`,
  },

  // File serving
  files: (jobId: string, filename: string) => `/files/${jobId}/${filename}`,
} as const;

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any,
  ) {
    super(`API Error ${status}: ${statusText}`);
    this.name = 'ApiError';
  }
}

export interface ApiRequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
}

/**
 * Base fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { params, ...fetchOptions } = options;

  // Build URL with query params
  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      searchParams.append(key, String(value));
    });
    url += `?${searchParams.toString()}`;
  }

  // Default headers
  const headers = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  };

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
    });

    // Handle non-OK responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(response.status, response.statusText, errorData);
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (!contentType?.includes('application/json')) {
      return null as T;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // Network or other errors
    throw new Error(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * API client methods
 */
export const apiClient = {
  /**
   * GET request
   */
  get: <T>(endpoint: string, options?: ApiRequestOptions): Promise<T> => {
    return apiFetch<T>(endpoint, { ...options, method: 'GET' });
  },

  /**
   * POST request
   */
  post: <T>(
    endpoint: string,
    data?: any,
    options?: ApiRequestOptions,
  ): Promise<T> => {
    return apiFetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * PUT request
   */
  put: <T>(
    endpoint: string,
    data?: any,
    options?: ApiRequestOptions,
  ): Promise<T> => {
    return apiFetch<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * PATCH request
   */
  patch: <T>(
    endpoint: string,
    data?: any,
    options?: ApiRequestOptions,
  ): Promise<T> => {
    return apiFetch<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * DELETE request
   */
  delete: <T>(endpoint: string, options?: ApiRequestOptions): Promise<T> => {
    return apiFetch<T>(endpoint, { ...options, method: 'DELETE' });
  },
};

export default apiClient;
