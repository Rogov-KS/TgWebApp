import React, { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Provider } from 'react-redux';
import { store } from '../store';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { initializeTheme, updateSystemTheme } from '../store/themeSlice';
import { AuthProvider } from '../../features/auth';
import { ModalProvider } from '../../shared/lib/contexts/ModalContext';

// Создаем QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 минут
      retry: 2,
    },
  },
});

// Компонент для инициализации темы
function ThemeInitializer({ children }: { children: React.ReactNode }) {
  const dispatch = useAppDispatch();
  const { currentTheme } = useAppSelector((state) => state.theme);

  useEffect(() => {
    // Инициализируем тему при загрузке приложения
    dispatch(initializeTheme());
  }, [dispatch]);

  useEffect(() => {
    // Подписываемся на изменения системной темы
    if (currentTheme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handler = () => dispatch(updateSystemTheme());

      mediaQuery.addEventListener('change', handler);
      return () => mediaQuery.removeEventListener('change', handler);
    }
  }, [currentTheme, dispatch]);

  return <>{children}</>;
}

interface AppProvidersProps {
  children: React.ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeInitializer>
          <AuthProvider>
            <ModalProvider>{children}</ModalProvider>
          </AuthProvider>
        </ThemeInitializer>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </Provider>
  );
}
