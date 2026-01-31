import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bot, Loader2, Settings } from 'lucide-react';
import { getAutoReplyConfig, updateAutoReplyConfig } from '../services/api';
import { useToast } from '../hooks/useToast';

export const AutoReplyToggle = () => {
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
      showToast(
        data.enabled
          ? 'Resposta automática ativada'
          : 'Resposta automática desativada',
        'success'
      );
    },
    onError: (error: any) => {
      showToast(
        error.response?.data?.detail || 'Erro ao atualizar configuração',
        'error'
      );
    },
  });

  const handleToggle = () => {
    if (!config) return;

    updateMutation.mutate({
      ...config,
      enabled: !config.enabled,
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200">
        <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
        <span className="text-sm text-gray-600">Carregando...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-red-50 rounded-lg border border-red-200">
        <span className="text-sm text-red-600">Erro ao carregar configuração</span>
      </div>
    );
  }

  const isEnabled = config?.enabled || false;

  return (
    <>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-lg border border-gray-200 shadow-sm">
          <Bot
            className={`h-5 w-5 ${
              isEnabled ? 'text-green-600' : 'text-gray-400'
            }`}
          />
          <div className="flex flex-col">
            <span className="text-xs text-gray-500">Resposta Automática</span>
            <span
              className={`text-sm font-medium ${
                isEnabled ? 'text-green-700' : 'text-gray-600'
              }`}
            >
              {isEnabled ? 'Ativada' : 'Desativada'}
            </span>
          </div>
          <button
            onClick={handleToggle}
            disabled={updateMutation.isPending}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
              isEnabled ? 'bg-green-600' : 'bg-gray-300'
            } ${updateMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                isEnabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>
      {ToastComponent}
    </>
  );
};

