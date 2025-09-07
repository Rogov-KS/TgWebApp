import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authAPI } from '../shared/api/client';

// Ключи для кэширования
export const queryKeys = {
  auth: {
    all: ['auth'] as const,
    helloWorld: () => [...queryKeys.auth.all, 'helloWorld'] as const,
    me: () => [...queryKeys.auth.all, 'me'] as const,
  },
};

// Хук для получения hello world
export const useHelloWorld = () => {
  return useQuery({
    queryKey: queryKeys.auth.helloWorld(),
    queryFn: async () => {
      const response = await authAPI.helloWorld();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 минут
    retry: 2,
  });
};

// Хук для логина
export const useLogin = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authAPI.login,
    onSuccess: () => {
      // Инвалидируем кэш пользователя после успешного логина
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.me() });
    },
  });
};

// Хук для регистрации
export const useRegister = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authAPI.register,
    onSuccess: () => {
      // Инвалидируем кэш пользователя после успешной регистрации
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.me() });
    },
  });
};

// Хук для логаута
export const useLogout = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authAPI.logout,
    onSuccess: () => {
      // Очищаем кэш после логаута
      queryClient.clear();
    },
  });
};

// Хук для получения информации о пользователе
export const useMe = () => {
  return useQuery({
    queryKey: queryKeys.auth.me(),
    queryFn: async () => {
      const response = await authAPI.me();
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // 10 минут
    retry: 1,
  });
};
