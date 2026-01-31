import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Mail,
  RefreshCw,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Filter,
  Trash2,
} from 'lucide-react';
import { EmailCard } from '../components/EmailCard';
import {
  getEmails,
  getSuggestions,
  checkNewEmails,
  clearAllEmails,
} from '../services/api';
import { useToast } from '../hooks/useToast';
import type { EmailSuggestion } from '../types';

export const Emails = () => {
  const [filterHasSuggestion, setFilterHasSuggestion] = useState<
    boolean | undefined
  >(undefined);
  const { showToast, ToastComponent } = useToast();
  const queryClient = useQueryClient();

  // Fetch emails
  const {
    data: emailsData,
    isLoading: isLoadingEmails,
    error: emailsError,
  } = useQuery({
    queryKey: ['emails', filterHasSuggestion],
    queryFn: () => getEmails(50, 0, filterHasSuggestion),
  });

  // Fetch pending suggestions for stats
  const {
    data: pendingSuggestionsData,
    isLoading: isLoadingPendingSuggestions,
  } = useQuery({
    queryKey: ['suggestions', 'pending'],
    queryFn: () => getSuggestions(100, 0, 'pending'),
  });

  // Fetch all suggestions (without status filter) to match with emails
  const {
    data: allSuggestionsData,
    isLoading: isLoadingAllSuggestions,
  } = useQuery({
    queryKey: ['suggestions', 'all'],
    queryFn: () => getSuggestions(100, 0), // Get suggestions without status filter (max 100)
  });

  // Check new emails mutation
  const checkEmailsMutation = useMutation({
    mutationFn: (limit: number) => checkNewEmails(limit),
    onSuccess: (data) => {
      showToast(
        `${data.processed} email(s) processado(s) com sucesso`,
        'success'
      );
      queryClient.invalidateQueries({ queryKey: ['emails'] });
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || 'Erro ao verificar novos emails',
        'error'
      );
    },
  });

  // Clear all emails mutation
  const clearAllEmailsMutation = useMutation({
    mutationFn: () => clearAllEmails(),
    onSuccess: (data) => {
      showToast(
        `${data.deleted_count} email(s) deletado(s) com sucesso`,
        'success'
      );
      queryClient.invalidateQueries({ queryKey: ['emails'] });
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || 'Erro ao deletar emails',
        'error'
      );
    },
  });

  const handleCheckNewEmails = () => {
    checkEmailsMutation.mutate(10);
  };

  const handleClearAllEmails = () => {
    if (
      !confirm(
        'Tem certeza que deseja deletar TODOS os emails? Esta ação é irreversível e deletará todos os emails e sugestões associadas.'
      )
    ) {
      return;
    }

    clearAllEmailsMutation.mutate();
  };

  const handleUpdate = () => {
    queryClient.invalidateQueries({ queryKey: ['emails'] });
    queryClient.invalidateQueries({ queryKey: ['suggestions'] });
  };

  // Create a map of email_id -> suggestion for quick lookup
  const suggestionsMap = new Map<string, EmailSuggestion>();
  if (allSuggestionsData?.suggestions) {
    allSuggestionsData.suggestions.forEach((suggestion) => {
      suggestionsMap.set(suggestion.email_id, suggestion);
    });
  }

  // Combine emails with their suggestions
  const emailsWithSuggestions =
    emailsData?.emails.map((email) => ({
      email,
      suggestion: email.has_suggestion && email.suggestion_id
        ? suggestionsMap.get(email.id)
        : undefined,
    })) || [];

  const pendingCount = pendingSuggestionsData?.suggestions.length || 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Mail className="h-8 w-8 text-primary-600" />
            Emails Recebidos
          </h1>
          <p className="text-gray-600 mt-2">
            Gerencie emails recebidos e aprove sugestões de resposta
          </p>
        </div>
        <div className="flex items-center gap-3">
          {emailsData && emailsData.total > 0 && (
            <button
              onClick={handleClearAllEmails}
              disabled={clearAllEmailsMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {clearAllEmailsMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Deletando...</span>
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4" />
                  <span>Deletar Todos</span>
                </>
              )}
            </button>
          )}
          <button
            onClick={handleCheckNewEmails}
            disabled={checkEmailsMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {checkEmailsMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Verificando...</span>
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4" />
                <span>Verificar Novos</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Stats and Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <Mail className="h-4 w-4" />
            <span className="text-sm">Total de Emails</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {emailsData?.total || 0}
          </p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <div className="flex items-center gap-2 text-yellow-700 mb-1">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">Pendentes</span>
          </div>
          <p className="text-2xl font-bold text-yellow-700">{pendingCount}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <div className="flex items-center gap-2 text-green-700 mb-1">
            <CheckCircle2 className="h-4 w-4" />
            <span className="text-sm">Com Sugestão</span>
          </div>
          <p className="text-2xl font-bold text-green-700">
            {emailsData?.emails.filter((e) => e.has_suggestion).length || 0}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="flex items-center gap-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Filtros:</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setFilterHasSuggestion(undefined)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                filterHasSuggestion === undefined
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Todos
            </button>
            <button
              onClick={() => setFilterHasSuggestion(true)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                filterHasSuggestion === true
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Com Sugestão
            </button>
            <button
              onClick={() => setFilterHasSuggestion(false)}
              className={`px-3 py-1 rounded text-sm transition-colors ${
                filterHasSuggestion === false
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Sem Sugestão
            </button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {(isLoadingEmails || isLoadingPendingSuggestions || isLoadingAllSuggestions) && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
          <span className="ml-3 text-gray-600">Carregando emails...</span>
        </div>
      )}

      {/* Error State */}
      {emailsError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="h-5 w-5" />
            <span>
              Erro ao carregar emails. Tente novamente ou verifique a conexão
              com o servidor.
            </span>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoadingEmails &&
        !emailsError &&
        emailsWithSuggestions.length === 0 && (
          <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <Mail className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum email encontrado
            </h3>
            <p className="text-gray-600 mb-4">
              {filterHasSuggestion === undefined
                ? 'Não há emails recebidos ainda. Clique em "Verificar Novos" para buscar emails.'
                : filterHasSuggestion
                ? 'Não há emails com sugestões pendentes.'
                : 'Não há emails sem sugestões.'}
            </p>
            <button
              onClick={handleCheckNewEmails}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Verificar Novos Emails
            </button>
          </div>
        )}

      {/* Email List */}
      {!isLoadingEmails &&
        !emailsError &&
        emailsWithSuggestions.length > 0 && (
          <div className="space-y-4">
            {emailsWithSuggestions.map(({ email, suggestion }) => (
              <EmailCard
                key={email.id}
                email={email}
                suggestion={suggestion}
                onUpdate={handleUpdate}
              />
            ))}
          </div>
        )}

      {ToastComponent}
    </div>
  );
};

