import axios from 'axios';
import type { EmailResponse, HistoryResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeFile = async (file: File): Promise<EmailResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<EmailResponse>('/analyze/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getHistory = async (
  limit: number = 50,
  category?: 'productive' | 'unproductive',
  full: boolean = true
): Promise<HistoryResponse> => {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  if (category) {
    params.append('category', category);
  }
  if (full) {
    params.append('full', 'true');
  }

  const response = await api.get<HistoryResponse>(`/rag/documents?${params.toString()}`);
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export interface ClearHistoryResponse {
  success: boolean;
  message: string;
  deleted_count: number;
}

export const clearHistory = async (): Promise<ClearHistoryResponse> => {
  const response = await api.delete<ClearHistoryResponse>('/rag/clear');
  return response.data;
};

