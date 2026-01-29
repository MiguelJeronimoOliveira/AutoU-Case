import { useQuery } from '@tanstack/react-query';
import { getHistory } from '../services/api';
import type { HistoryResponse } from '../types';

export const useEmailHistory = (
  limit: number = 50,
  category?: 'productive' | 'unproductive',
  enabled: boolean = true
) => {
  return useQuery<HistoryResponse>({
    queryKey: ['emailHistory', limit, category],
    queryFn: () => getHistory(limit, category),
    enabled,
    staleTime: 30000, // 30 segundos
    refetchOnWindowFocus: false,
  });
};

