import axios from 'axios';
import type { Message, SearchResult, SearchFilters, AnalyticsData } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Chat API
export const chatAPI = {
  sendMessage: async (
    message: string,
    sessionId?: string
  ): Promise<{ response: string; sources: any[]; entities: any[] }> => {
    const response = await apiClient.post('/api/chat', {
      message,
      session_id: sessionId,
    });
    return response.data;
  },

  getChatHistory: async (sessionId: string): Promise<Message[]> => {
    const response = await apiClient.get(`/api/chat/history/${sessionId}`);
    return response.data;
  },

  createSession: async (): Promise<{ session_id: string }> => {
    const response = await apiClient.post('/api/chat/session');
    return response.data;
  },
};

// Search API
export const searchAPI = {
  search: async (
    query: string,
    filters?: SearchFilters,
    limit: number = 10
  ): Promise<SearchResult[]> => {
    const response = await apiClient.post('/api/search', {
      query,
      filters,
      limit,
    });
    return response.data;
  },

  semanticSearch: async (
    query: string,
    topK: number = 5
  ): Promise<SearchResult[]> => {
    const response = await apiClient.post('/api/search/semantic', {
      query,
      top_k: topK,
    });
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getTrends: async (): Promise<AnalyticsData> => {
    const response = await apiClient.get('/api/analytics/trends');
    return response.data;
  },

  getMissionComparison: async (missions: string[]) => {
    const response = await apiClient.post('/api/analytics/missions', {
      missions,
    });
    return response.data;
  },

  getEntityDistribution: async () => {
    const response = await apiClient.get('/api/analytics/entities');
    return response.data;
  },
};

// Entity Extraction API
export const entityAPI = {
  extractEntities: async (text: string) => {
    const response = await apiClient.post('/api/entities/extract', { text });
    return response.data;
  },
};

export default apiClient;
