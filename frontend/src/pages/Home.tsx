import { useState } from 'react';
import { FileUpload } from '../components/FileUpload';
import { AnalysisResult } from '../components/AnalysisResult';
import { useToast } from '../hooks/useToast';
import type { EmailResponse } from '../types';

export const Home = () => {
  const [analysisResult, setAnalysisResult] = useState<EmailResponse | null>(
    null
  );
  const { showToast, ToastComponent } = useToast();

  const handleAnalysisComplete = (response: EmailResponse) => {
    setAnalysisResult(response);
    if (response.success) {
      showToast('Email analisado com sucesso!', 'success');
    }
  };

  const handleError = (message: string) => {
    showToast(message, 'error');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold text-gray-900">
          Análise de Emails
        </h1>
        <p className="text-gray-600">
          Envie um arquivo .txt ou .pdf para receber uma sugestão de resposta
          automática
        </p>
      </div>

      <FileUpload
        onAnalysisComplete={handleAnalysisComplete}
        onError={handleError}
      />

      {analysisResult?.analysis && (
        <div className="mt-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Resultado da Análise
          </h2>
          <AnalysisResult analysis={analysisResult.analysis} />
        </div>
      )}

      {analysisResult?.error && (
        <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{analysisResult.error}</p>
        </div>
      )}

      {ToastComponent}
    </div>
  );
};

