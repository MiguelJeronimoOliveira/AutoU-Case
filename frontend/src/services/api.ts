import axios from 'axios';
import type { EmailResponse, HistoryResponse } from '../types';

const API_BASE_URL = (import.meta.env?.VITE_API_URL as string) || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeFile = async (file: File): Promise<EmailResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<EmailResponse>('/api/v1/analyze/upload', formData, {
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

  const response = await api.get<HistoryResponse>(`/api/v1/rag/documents?${params.toString()}`);
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/api/v1/health');
  return response.data;
};

export interface ClearHistoryResponse {
  success: boolean;
  message: string;
  deleted_count: number;
}

export const clearHistory = async (): Promise<ClearHistoryResponse> => {
  const response = await api.delete<ClearHistoryResponse>('/api/v1/rag/clear');
  return response.data;
};

// Email Flow API
import type {
  EmailListResponse,
  ReceivedEmail,
  EmailSuggestion,
  SuggestionListResponse,
  SuggestionWithEmail,
} from '../types';

export const getEmails = async (
  limit: number = 50,
  offset: number = 0,
  hasSuggestion?: boolean
): Promise<EmailListResponse> => {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());
  if (hasSuggestion !== undefined) {
    params.append('has_suggestion', hasSuggestion.toString());
  }

  const response = await api.get<EmailListResponse>(
    `/api/v1/emails?${params.toString()}`
  );
  return response.data;
};

export const getEmail = async (emailId: string): Promise<ReceivedEmail> => {
  const response = await api.get<ReceivedEmail>(`/api/v1/emails/${emailId}`);
  return response.data;
};

export const getSuggestions = async (
  limit: number = 50,
  offset: number = 0,
  status?: 'pending' | 'approved' | 'rejected' | 'sent'
): Promise<SuggestionListResponse> => {
  const params = new URLSearchParams();
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());
  if (status) {
    params.append('status', status);
  }

  const response = await api.get<SuggestionListResponse>(
    `/api/v1/suggestions?${params.toString()}`
  );
  return response.data;
};

export const getSuggestion = async (
  suggestionId: string
): Promise<SuggestionWithEmail> => {
  const response = await api.get<SuggestionWithEmail>(
    `/api/v1/suggestions/${suggestionId}`
  );
  return response.data;
};

export const getSuggestionByEmailId = async (
  emailId: string
): Promise<EmailSuggestion> => {
  const response = await api.get<EmailSuggestion>(
    `/api/v1/emails/${emailId}/suggestion`
  );
  return response.data;
};

export interface ApproveSuggestionRequest {
  suggestion_id: string;
  send_email: boolean;
}

export interface ApproveSuggestionResponse {
  success: boolean;
  message: string;
}

export const approveSuggestion = async (
  suggestionId: string,
  sendEmail: boolean = true
): Promise<ApproveSuggestionResponse> => {
  const response = await api.post<ApproveSuggestionResponse>(
    `/api/v1/suggestions/${suggestionId}/approve`,
    {
      suggestion_id: suggestionId,
      send_email: sendEmail,
    }
  );
  return response.data;
};

export interface RejectSuggestionResponse {
  success: boolean;
  message: string;
}

export const rejectSuggestion = async (
  suggestionId: string
): Promise<RejectSuggestionResponse> => {
  const response = await api.post<RejectSuggestionResponse>(
    `/api/v1/suggestions/${suggestionId}/reject`
  );
  return response.data;
};

export interface CheckEmailsResponse {
  success: boolean;
  message: string;
  fetched: number;
  processed: number;
}

export const checkNewEmails = async (
  limit: number = 10
): Promise<CheckEmailsResponse> => {
  const response = await api.post<CheckEmailsResponse>(
    `/api/v1/emails/check?limit=${limit}`
  );
  return response.data;
};

export interface DeleteEmailResponse {
  success: boolean;
  message: string;
}

export const deleteEmail = async (
  emailId: string
): Promise<DeleteEmailResponse> => {
  const response = await api.delete<DeleteEmailResponse>(
    `/api/v1/emails/${emailId}`
  );
  return response.data;
};

export interface ClearAllEmailsResponse {
  success: boolean;
  message: string;
  deleted_count: number;
}

export const clearAllEmails = async (): Promise<ClearAllEmailsResponse> => {
  const response = await api.delete<ClearAllEmailsResponse>('/api/v1/emails');
  return response.data;
};

