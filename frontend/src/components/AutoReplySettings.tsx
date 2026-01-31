import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bot, Loader2, Info } from 'lucide-react';
import { getAutoReplyConfig, updateAutoReplyConfig } from '../services/api';
import { useToast } from '../hooks/useToast';
import type { AutoReplyConfig } from '../types';

export const AutoReplySettings = () => {
  const { showToast, ToastComponent } = useToast();
  const queryClient = useQueryClient();

  // Fetch current config
  const {
    data: config,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['autoReplyConfig'],
    queryFn: getAutoReplyConfig,
  });

  // Update config mutation
  const updateMutation = useMutation({
    mutationFn: updateAutoReplyConfig,
    onSuccess: (data) => {
      queryClient.setQueryData(['autoReplyConfig'], data);
      showToast('Configurações salvas com sucesso!', 'success');
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || 'Erro ao salvar configurações',
        'error'
      );
    },
  });

  const handleToggle = (field: keyof AutoReplyConfig, value: boolean) => {
    if (!config) return;

    updateMutation.mutate({
      ...config,
      [field]: value,
    });
  };

  const handleMinConfidenceChange = (value: number) => {
    if (!config) return;

    // Clamp value between 0 and 1
    const clampedValue = Math.max(0, Math.min(1, value));

    updateMutation.mutate({
      ...config,
      min_confidence: clampedValue,
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center gap-2 py-8">
        <Loader2 className="h-5 w-5 animate-spin text-gray-500" />
        <span className="text-sm text-gray-600">Carregando configurações...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 px-4 py-3 bg-red-50 rounded-lg border border-red-200">
        <span className="text-sm text-red-600">
          Erro ao carregar configurações. Tente recarregar a página.
        </span>
      </div>
    );
  }

  if (!config) {
    return null;
  }

  const isEnabled = config.enabled || false;
  const onlyProductive = config.only_productive || false;
  const minConfidence = config.min_confidence || 0.7;

  return (
    <>
      <div className="space-y-6">
        {/* Enable/Disable Auto-Reply */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Bot
                className={`h-5 w-5 ${
                  isEnabled ? 'text-green-600' : 'text-gray-400'
                }`}
              />
              <h3 className="text-lg font-semibold text-gray-900">
                Ativar Resposta Automática
              </h3>
            </div>
            <p className="text-sm text-gray-600">
              Quando ativado, o sistema responderá automaticamente aos emails
              recebidos de acordo com as regras configuradas abaixo.
            </p>
          </div>
          <button
            onClick={() => handleToggle('enabled', !isEnabled)}
            disabled={updateMutation.isPending}
            className={`relative ml-4 inline-flex h-7 w-12 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
              isEnabled ? 'bg-green-600' : 'bg-gray-300'
            } ${updateMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <span
              className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
                isEnabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Only Productive Emails */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              Apenas Emails Produtivos
            </h3>
            <p className="text-sm text-gray-600">
              Quando ativado, apenas emails classificados como produtivos receberão
              resposta automática. Emails não produtivos serão ignorados.
            </p>
          </div>
          <button
            onClick={() => handleToggle('only_productive', !onlyProductive)}
            disabled={updateMutation.isPending || !isEnabled}
            className={`relative ml-4 inline-flex h-7 w-12 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
              onlyProductive ? 'bg-green-600' : 'bg-gray-300'
            } ${
              updateMutation.isPending || !isEnabled
                ? 'opacity-50 cursor-not-allowed'
                : ''
            }`}
          >
            <span
              className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
                onlyProductive ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Minimum Confidence */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="text-lg font-semibold text-gray-900">
              Confiança Mínima
            </h3>
            <div className="group relative">
              <Info className="h-4 w-4 text-gray-400 cursor-help" />
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg z-10">
                A confiança mínima determina o nível de certeza necessário para
                que o sistema responda automaticamente. Valores mais altos são
                mais conservadores.
              </div>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Configure o nível mínimo de confiança (0.0 a 1.0) necessário para
            enviar uma resposta automática. Valor atual: <strong>{minConfidence.toFixed(2)}</strong>
          </p>
          <div className="space-y-3">
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={minConfidence}
              onChange={(e) => handleMinConfidenceChange(parseFloat(e.target.value))}
              disabled={updateMutation.isPending || !isEnabled}
              className={`w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer ${
                updateMutation.isPending || !isEnabled
                  ? 'opacity-50 cursor-not-allowed'
                  : ''
              }`}
              style={{
                background: `linear-gradient(to right, #10b981 0%, #10b981 ${
                  minConfidence * 100
                }%, #e5e7eb ${minConfidence * 100}%, #e5e7eb 100%)`,
              }}
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0.0 (Menos Conservador)</span>
              <span>1.0 (Mais Conservador)</span>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={minConfidence}
                onChange={(e) =>
                  handleMinConfidenceChange(parseFloat(e.target.value) || 0)
                }
                disabled={updateMutation.isPending || !isEnabled}
                className={`w-24 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                  updateMutation.isPending || !isEnabled
                    ? 'opacity-50 cursor-not-allowed bg-gray-100'
                    : ''
                }`}
              />
              <button
                onClick={() => handleMinConfidenceChange(0.7)}
                disabled={updateMutation.isPending || !isEnabled}
                className="px-3 py-2 text-sm text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Padrão (0.70)
              </button>
            </div>
          </div>
        </div>

        {/* Status Summary */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">
            Status Atual
          </h4>
          <ul className="space-y-1 text-sm text-blue-800">
            <li>
              • Resposta automática:{' '}
              <strong>{isEnabled ? 'Ativada' : 'Desativada'}</strong>
            </li>
            {isEnabled && (
              <>
                <li>
                  • Filtro de emails:{' '}
                  <strong>
                    {onlyProductive
                      ? 'Apenas produtivos'
                      : 'Todos os emails'}
                  </strong>
                </li>
                <li>
                  • Confiança mínima: <strong>{minConfidence.toFixed(2)}</strong>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
      {ToastComponent}
    </>
  );
};

