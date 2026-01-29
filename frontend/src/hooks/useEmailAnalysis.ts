import { useMutation } from '@tanstack/react-query';
import { analyzeFile } from '../services/api';
import type { EmailResponse } from '../types';

export const useEmailAnalysis = () => {
  return useMutation({
    mutationFn: (file: File) => analyzeFile(file),
    onError: (error: Error) => {
      console.error('Erro ao analisar email:', error);
    },
  });
};

