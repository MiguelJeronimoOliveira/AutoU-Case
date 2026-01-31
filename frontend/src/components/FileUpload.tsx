import { useRef, useState } from 'react';
import { Upload, FileText, X, Loader2 } from 'lucide-react';
import { useEmailAnalysis } from '../hooks/useEmailAnalysis';
import type { EmailResponse } from '../types';

interface FileUploadProps {
  onAnalysisComplete: (response: EmailResponse) => void;
  onFileSelect?: () => void;
  onError?: (message: string) => void;
}

export const FileUpload = ({ onAnalysisComplete, onFileSelect, onError }: FileUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const { mutate: analyzeEmail, isPending } = useEmailAnalysis();

  const handleFileSelect = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (extension !== 'txt' && extension !== 'pdf') {
      const errorMsg = 'Por favor, selecione apenas arquivos .txt ou .pdf';
      if (onError) {
        onError(errorMsg);
      } else {
        alert(errorMsg);
      }
      return;
    }
    setSelectedFile(file);
    // Notifica que um novo arquivo foi selecionado para limpar resultado anterior
    if (onFileSelect) {
      onFileSelect();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const handleUpload = () => {
    if (!selectedFile) return;

    analyzeEmail(selectedFile, {
      onSuccess: (response) => {
        onAnalysisComplete(response);
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      },
      onError: (error: any) => {
        console.error('Erro ao analisar:', error);
        const errorMsg =
          error?.response?.data?.detail ||
          error?.message ||
          'Erro ao analisar o arquivo. Tente novamente.';
        if (onError) {
          onError(errorMsg);
        } else {
          alert(errorMsg);
        }
      },
    });
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full">
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 transition-colors ${
          dragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        } ${isPending ? 'opacity-50 pointer-events-none' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.pdf"
          onChange={handleFileChange}
          className="hidden"
          disabled={isPending}
        />

        {!selectedFile ? (
          <div className="text-center">
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-700 mb-2">
              Arraste e solte seu arquivo aqui
            </p>
            <p className="text-sm text-gray-500 mb-4">ou</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
              disabled={isPending}
            >
              Selecionar Arquivo
            </button>
            <p className="text-xs text-gray-400 mt-4">
              Formatos suportados: .txt, .pdf
            </p>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-primary-600" />
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleRemoveFile}
                className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                disabled={isPending}
              >
                <X className="h-5 w-5" />
              </button>
              <button
                onClick={handleUpload}
                disabled={isPending}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Analisando...
                  </>
                ) : (
                  'Analisar Email'
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

