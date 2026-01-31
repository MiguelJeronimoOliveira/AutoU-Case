import { useMutation } from '@tanstack/react-query';
import { analyzeFile } from '../services/api';

export const useEmailAnalysis = () => {
  return useMutation({
    mutationFn: (file: File) => analyzeFile(file),
    onError: (error: Error) => {
      console.error('Erro ao analisar email:', error);
    },
  });
};

