import { useEmailHistory } from '../hooks/useEmailHistory';
import { Loader2, RefreshCw, Filter, Eye, X } from 'lucide-react';
import { useState } from 'react';
import { clsx } from 'clsx';
import type { EmailCategory, HistoryDocument } from '../types';

export const EmailHistory = () => {
  const [categoryFilter, setCategoryFilter] = useState<
    'productive' | 'unproductive' | undefined
  >(undefined);
  const [limit, setLimit] = useState(50);
  const [selectedDoc, setSelectedDoc] = useState<HistoryDocument | null>(null);

  const {
    data: historyData,
    isLoading,
    isError,
    refetch,
    isRefetching,
  } = useEmailHistory(limit, categoryFilter);

  const getCategoryBadge = (category: EmailCategory) => {
    const isProductive = category === 'productive';
    return (
      <span
        className={clsx(
          'px-3 py-1 rounded-full text-xs font-medium',
          isProductive
            ? 'bg-green-100 text-green-800'
            : 'bg-blue-100 text-blue-800'
        )}
      >
        {isProductive ? 'Produtivo' : 'Não Produtivo'}
      </span>
    );
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('pt-BR', {
        dateStyle: 'short',
        timeStyle: 'short',
      }).format(date);
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        <span className="ml-3 text-gray-600">Carregando histórico...</span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">Erro ao carregar histórico</p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  const documents = historyData?.documents || [];

  return (
    <div className="space-y-6">
      {/* Filtros e Controles */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center gap-2">
          <Filter className="h-5 w-5 text-gray-500" />
          <span className="font-medium text-gray-700">Filtros:</span>
          <button
            onClick={() => setCategoryFilter(undefined)}
            className={clsx(
              'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
              categoryFilter === undefined
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            )}
          >
            Todos
          </button>
          <button
            onClick={() => setCategoryFilter('productive')}
            className={clsx(
              'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
              categoryFilter === 'productive'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            )}
          >
            Produtivos
          </button>
          <button
            onClick={() => setCategoryFilter('unproductive')}
            className={clsx(
              'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
              categoryFilter === 'unproductive'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            )}
          >
            Não Produtivos
          </button>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-700">Limite:</label>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
          >
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={200}>200</option>
          </select>
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="p-2 text-gray-600 hover:text-primary-600 transition-colors disabled:opacity-50"
            title="Atualizar"
          >
            <RefreshCw
              className={clsx('h-5 w-5', isRefetching && 'animate-spin')}
            />
          </button>
        </div>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-white rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600">Total de Emails</p>
          <p className="text-2xl font-bold text-gray-900">
            {historyData?.count || 0}
          </p>
        </div>
        <div className="p-4 bg-white rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600">Produtivos</p>
          <p className="text-2xl font-bold text-green-600">
            {documents.filter((d) => d.category === 'productive').length}
          </p>
        </div>
        <div className="p-4 bg-white rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600">Não Produtivos</p>
          <p className="text-2xl font-bold text-blue-600">
            {documents.filter((d) => d.category === 'unproductive').length}
          </p>
        </div>
      </div>

      {/* Lista de Emails */}
      {documents.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-gray-600">Nenhum email encontrado no histórico</p>
        </div>
      ) : (
        <div className="space-y-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="p-6 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getCategoryBadge(doc.category)}
                  <span className="text-sm text-gray-500">
                    {formatDate(doc.created_at)}
                  </span>
                </div>
                <button
                  onClick={() => setSelectedDoc(doc)}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
                >
                  <Eye className="h-4 w-4" />
                  Ver Completo
                </button>
              </div>

              <div className="space-y-3">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">
                    Email:
                  </h4>
                  <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded border border-gray-200 line-clamp-3">
                    {doc.email_content || 'Sem conteúdo'}
                  </p>
                </div>

                {doc.response && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">
                      Resposta Sugerida:
                    </h4>
                    <p className="text-sm text-gray-800 bg-primary-50 p-3 rounded border border-primary-200">
                      {doc.response}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal para exibir conteúdo completo */}
      {selectedDoc && (() => {
        let fullEmailContent = selectedDoc.email_content || '';
        
        if (selectedDoc.full_document) {
          const match = selectedDoc.full_document.match(/^Email:\s*(.+?)(?:\nResposta:|$)/s);
          if (match && match[1]) {
            fullEmailContent = match[1].trim();
          }
        }

        return (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  {getCategoryBadge(selectedDoc.category)}
                  <span className="text-sm text-gray-500">
                    {formatDate(selectedDoc.created_at)}
                  </span>
                </div>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">
                    Email Completo:
                  </h3>
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <p className="text-sm text-gray-900 whitespace-pre-wrap break-words">
                      {fullEmailContent || 'Sem conteúdo'}
                    </p>
                  </div>
                </div>

                {selectedDoc.response && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      Resposta Sugerida Completa:
                    </h3>
                    <div className="bg-primary-50 p-4 rounded-lg border border-primary-200">
                      <p className="text-sm text-gray-800 whitespace-pre-wrap break-words">
                        {selectedDoc.response}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <div className="p-6 border-t border-gray-200 flex justify-end">
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Fechar
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
};

