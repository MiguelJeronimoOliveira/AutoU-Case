import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Database, Trash2, Loader2, AlertTriangle, History } from 'lucide-react';
import { clearAllEmails, clearHistory } from '../services/api';
import { useToast } from '../hooks/useToast';

export const StorageSettings = () => {
  const { showToast, ToastComponent } = useToast();
  const queryClient = useQueryClient();

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

  // Clear history mutation
  const clearHistoryMutation = useMutation({
    mutationFn: () => clearHistory(),
    onSuccess: (data) => {
      showToast(
        `Histórico limpo com sucesso! ${data.deleted_count} documentos removidos.`,
        'success'
      );
      queryClient.invalidateQueries({ queryKey: ['rag', 'documents'] });
      // Reload after a short delay to show the toast
      setTimeout(() => {
        window.location.reload();
      }, 1500);
    },
    onError: (error: any) => {
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        'Erro ao limpar histórico';
      showToast(errorMessage, 'error');
    },
  });

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

  const handleClearHistory = () => {
    if (
      !confirm(
        'Tem certeza que deseja limpar todo o histórico? Esta ação não pode ser desfeita e removerá todos os documentos do histórico de análises.'
      )
    ) {
      return;
    }

    clearHistoryMutation.mutate();
  };

  return (
    <>
      <div className="space-y-6">
        <p className="text-gray-600">
          Gerencie o armazenamento de dados do sistema. Use com cuidado, pois
          essas ações são irreversíveis.
        </p>

        {/* Clear All Emails */}
        <div className="p-4 bg-red-50 rounded-lg border border-red-200">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Trash2 className="h-5 w-5 text-red-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Deletar Todos os Emails
                </h3>
              </div>
              <p className="text-sm text-gray-600 mb-2">
                Remove permanentemente todos os emails recebidos e suas sugestões
                associadas do sistema. Esta ação não pode ser desfeita.
              </p>
              <div className="flex items-center gap-2 text-xs text-red-700 bg-red-100 px-2 py-1 rounded">
                <AlertTriangle className="h-3 w-3" />
                <span>Ação irreversível</span>
              </div>
            </div>
          </div>
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
                <span>Deletar Todos os Emails</span>
              </>
            )}
          </button>
        </div>

        {/* Clear History */}
        <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <History className="h-5 w-5 text-orange-600" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Limpar Histórico de Análises
                </h3>
              </div>
              <p className="text-sm text-gray-600 mb-2">
                Remove permanentemente todo o histórico de análises de emails do
                sistema. Isso não afeta os emails recebidos, apenas o histórico
                de análises realizadas.
              </p>
              <div className="flex items-center gap-2 text-xs text-orange-700 bg-orange-100 px-2 py-1 rounded">
                <AlertTriangle className="h-3 w-3" />
                <span>Ação irreversível</span>
              </div>
            </div>
          </div>
          <button
            onClick={handleClearHistory}
            disabled={clearHistoryMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {clearHistoryMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Limpando...</span>
              </>
            ) : (
              <>
                <History className="h-4 w-4" />
                <span>Limpar Histórico</span>
              </>
            )}
          </button>
        </div>

        {/* Info Box */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-start gap-3">
            <Database className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-blue-900 mb-1">
                Sobre o Armazenamento
              </h4>
              <ul className="space-y-1 text-sm text-blue-800">
                <li>
                  • <strong>Emails:</strong> Armazenam os emails recebidos e suas
                  sugestões de resposta
                </li>
                <li>
                  • <strong>Histórico:</strong> Armazena o histórico de análises
                  realizadas pelo sistema
                </li>
                <li>
                  • As ações de limpeza são permanentes e não podem ser desfeitas
                </li>
                <li>
                  • Recomenda-se fazer backup antes de executar essas ações
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      {ToastComponent}
    </>
  );
};

