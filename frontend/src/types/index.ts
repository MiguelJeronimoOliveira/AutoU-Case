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

// Email Flow Types
export interface ReceivedEmail {
  id: string;
  message_id?: string | null;
  subject: string;
  sender: string;
  recipient: string;
  content: string;
  received_at: string;
  category?: EmailCategory | null;
  confidence?: number | null;
  has_suggestion: boolean;
  suggestion_id?: string | null;
}

export interface EmailSuggestion {
  id: string;
  email_id: string;
  suggested_response: string;
  status: 'pending' | 'approved' | 'rejected' | 'sent';
  created_at: string;
  approved_at?: string | null;
  sent_at?: string | null;
}

export interface EmailListResponse {
  emails: ReceivedEmail[];
  total: number;
}

export interface SuggestionListResponse {
  suggestions: EmailSuggestion[];
  total: number;
}

export interface SuggestionWithEmail {
  suggestion: EmailSuggestion;
  email: ReceivedEmail;
}

export interface AutoReplyConfig {
  enabled: boolean;
  only_productive: boolean;
  min_confidence: number;
}

