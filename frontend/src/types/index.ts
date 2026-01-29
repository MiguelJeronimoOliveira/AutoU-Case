export type EmailCategory = 'productive' | 'unproductive';

export interface EmailAnalysis {
  content: string;
  full_content?: string | null;
  category: EmailCategory;
  confidence: number;
  suggested_response: string | null;
  reasoning: string | null;
}

export interface EmailResponse {
  success: boolean;
  analysis: EmailAnalysis | null;
  error: string | null;
}

export interface HistoryDocument {
  id: string;
  category: EmailCategory;
  created_at: string;
  email_content: string;
  response: string;
  full_document?: string;
}

export interface HistoryResponse {
  success: boolean;
  count: number;
  limit: number;
  category_filter: string | null;
  documents: HistoryDocument[];
}

