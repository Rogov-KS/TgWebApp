import { useQuery } from '@tanstack/react-query';
import { authAPI } from './client';

export const useHelloWorld = () => {
  return useQuery({
    queryKey: ['helloWorld'],
    queryFn: () => authAPI.helloWorld(),
    staleTime: 5 * 60 * 1000, // 5 минут
    retry: 1,
  });
};
