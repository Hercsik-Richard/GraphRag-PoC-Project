/**
 * Application constants and configuration values
 */

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
export const API_REQUEST_TIMEOUT = 60000;
export const CHAT_REQUEST_TIMEOUT = 900000;

export type ModelProvider = 'ollama' | 'gemini' | 'openrouter';

export const MODEL_PROVIDER_OPTIONS: Array<{
  value: ModelProvider;
  label: string;
  detail: string;
}> = [
  { value: 'ollama', label: 'Qwen', detail: 'Ollama' },
  { value: 'gemini', label: 'Gemini', detail: 'Google' },
  { value: 'openrouter', label: 'OpenRouter', detail: 'API' },
];

// API Endpoints
export const API_ENDPOINTS = {
  // Chat endpoints
  CHAT: {
    CONVERSATIONS: '/api/chat/conversations',
    CONVERSATION: (id: string) => `/api/chat/conversations/${id}`,
    MESSAGES: (id: string) => `/api/chat/conversations/${id}/messages`,
    QUERY: (id: string) => `/api/chat/conversations/${id}/query`,
  },
  // Graph endpoints
  GRAPH: {
    FULL: '/api/graph/full',
    STATS: '/api/graph/stats',
    DIAGNOSTICS: '/api/graph/diagnostics',
  },
  // Index endpoints
  INDEX: {
    UPLOAD: '/api/index/upload',
    CURRENT: '/api/index/current',
    STATUS: '/api/index/status',
    PROGRESS: (id: string) => `/api/index/progress/${id}`,
  },
} as const;

// UI Constants
export const UI_CONSTANTS = {
  // Layout
  SIDEBAR_WIDTH: 280,
  DETAILS_WIDTH: 320,
  
  // Limits
  MAX_MESSAGE_LENGTH: 2000,
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  
  // Delays
  DEBOUNCE_DELAY: 300,
  TOAST_DURATION: 3000,
  
  // React Flow
  GRAPH: {
    NODE_WIDTH: 180,
    NODE_HEIGHT: 80,
    EDGE_ANIMATED: true,
    FIT_VIEW_PADDING: 0.2,
  },
} as const;

// Message roles
export const MESSAGE_ROLES = {
  USER: 'user',
  ASSISTANT: 'assistant',
} as const;

// File upload constraints
export const FILE_UPLOAD = {
  ACCEPTED_TYPES: ['.txt'],
  MAX_SIZE: UI_CONSTANTS.MAX_FILE_SIZE,
  MAX_SIZE_MB: 10,
} as const;
