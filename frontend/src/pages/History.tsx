import { useState } from 'react';
import { EmailHistory } from '../components/EmailHistory';
import { useToast } from '../hooks/useToast';
import { clearHistory } from '../services/api';

export const History = () => {
  const [isClearing, setIsClearing] = useState(false);
  const { showToast, ToastComponent } = useToast();

  const handleClearHistory = async () => {
    if (!confirm('Tem certeza que deseja limpar todo o histórico? Esta ação não pode ser desfeita.')) {
      return;
    }

    setIsClearing(true);
    try {
      const result = await clearHistory();
      showToast(
        `Histórico limpo com sucesso! ${result.deleted_count} documentos removidos.`,
        'success'
      );
      window.location.reload();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Erro ao limpar histórico';
      showToast(errorMessage, 'error');
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Histórico de Emails
            </h1>
            <p className="text-gray-600">
              Visualize todos os emails analisados com suas categorias e sugestões
              de resposta
            </p>
          </div>
          <button
            onClick={handleClearHistory}
            disabled={isClearing}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isClearing ? 'Limpando...' : 'Limpar Histórico'}
          </button>
        </div>
      </div>

      <EmailHistory />
      {ToastComponent}
    </div>
  );
};

