import { CheckCircle2, XCircle, TrendingUp, MessageSquare, Mail } from 'lucide-react';
import type { EmailAnalysis } from '../types';
import { clsx } from 'clsx';

interface AnalysisResultProps {
  analysis: EmailAnalysis;
}

export const AnalysisResult = ({ analysis }: AnalysisResultProps) => {
  const isProductive = analysis.category === 'productive';
  const confidencePercentage = Math.round(analysis.confidence * 100);
  const emailContent = analysis.full_content || analysis.content;

  return (
    <div className="space-y-6">
      {/* Categoria e Confiança */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          className={clsx(
            'p-6 rounded-lg border-2',
            isProductive
              ? 'bg-green-50 border-green-200'
              : 'bg-blue-50 border-blue-200'
          )}
        >
          <div className="flex items-center gap-3 mb-2">
            {isProductive ? (
              <CheckCircle2 className="h-6 w-6 text-green-600" />
            ) : (
              <XCircle className="h-6 w-6 text-blue-600" />
            )}
            <h3 className="text-lg font-semibold text-gray-900">
              Categoria: {isProductive ? 'Produtivo' : 'Não Produtivo'}
            </h3>
          </div>
          <p className="text-sm text-gray-600">
            {isProductive
              ? 'Este email requer uma ação ou resposta.'
              : 'Este email não requer ação imediata.'}
          </p>
        </div>

        <div className="p-6 rounded-lg border-2 border-gray-200 bg-white">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="h-6 w-6 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Confiança</h3>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-primary-600">
                {confidencePercentage}%
              </span>
            </div>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-primary-600 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${confidencePercentage}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Reasoning */}
      {analysis.reasoning && (
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-2">Raciocínio</h4>
          <p className="text-sm text-gray-700">{analysis.reasoning}</p>
        </div>
      )}

      {/* Preview Completo do Email - ANTES da Resposta */}
      <div className="p-6 bg-white rounded-lg border-2 border-gray-200 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <Mail className="h-6 w-6 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Conteúdo do Email
          </h3>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 max-h-96 overflow-y-auto">
          <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
            {emailContent}
          </p>
        </div>
      </div>

      {/* Sugestão de Resposta */}
      {analysis.suggested_response && (
        <div className="p-6 bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg border-2 border-primary-200">
          <div className="flex items-center gap-3 mb-4">
            <MessageSquare className="h-6 w-6 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Sugestão de Resposta
            </h3>
          </div>
          <div className="bg-white p-4 rounded-lg border border-primary-200">
            <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
              {analysis.suggested_response}
            </p>
          </div>
          <button
            onClick={async () => {
              try {
                await navigator.clipboard.writeText(
                  analysis.suggested_response || ''
                );
                // Mostrar feedback visual seria melhor, mas por simplicidade mantemos o alert
                alert('Resposta copiada para a área de transferência!');
              } catch (err) {
                console.error('Erro ao copiar:', err);
                alert('Erro ao copiar. Tente novamente.');
              }
            }}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
          >
            Copiar Resposta
          </button>
        </div>
      )}
    </div>
  );
};

