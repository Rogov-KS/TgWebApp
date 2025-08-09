import React, { createContext, useContext, useReducer, useEffect, ReactNode, useRef, useCallback } from 'react';
import { authAPI, leaderboardAPI } from '../api/client';
import type { User, UserAuth, UserLogin, AuthState } from '../types/auth';

// Типы действий
type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'LOGOUT' };

// Начальное состояние
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Reducer для управления состоянием
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        error: null,
      };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        error: null,
      };
    default:
      return state;
  }
}

// Контекст
interface AuthContextType extends AuthState {
  login: (data: UserLogin) => Promise<void>;
  register: (data: UserAuth) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  updateUserMaxScore: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Провайдер
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const checkAuthInProgress = useRef(false);
  const lastCheckTime = useRef<number>(0);
  const lastMeRequestTime = useRef<number>(0);
  const authCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const currentAuthState = useRef<{ isAuthenticated: boolean; user: User | null }>({
    isAuthenticated: false,
    user: null
  });
  const CHECK_AUTH_DEBOUNCE = 2000; // 2 секунды между запросами
  const ME_REQUEST_INTERVAL = 5000; // 5 секунд между запросами /me для неавторизованных пользователей
  const AUTH_CHECK_INTERVAL = 100; // 0.1 секунды для проверки состояния авторизации

  // Обновляем ref при изменении состояния
  useEffect(() => {
    currentAuthState.current = {
      isAuthenticated: state.isAuthenticated,
      user: state.user,
    };
  }, [state.isAuthenticated, state.user]);

  // Проверка авторизации с дебаунсингом
  const checkAuth = useCallback(async () => {
    const now = Date.now();

    // Проверяем, не слишком ли часто вызывается функция
    if (checkAuthInProgress.current) {
      return;
    }

    // Проверяем дебаунсинг
    if (now - lastCheckTime.current < CHECK_AUTH_DEBOUNCE) {
      return;
    }

    try {
      checkAuthInProgress.current = true;
      lastCheckTime.current = now;

      dispatch({ type: 'SET_LOADING', payload: true });
      console.log('🔐 Checking authentication...');

      const response = await authAPI.me();

      // Получаем актуальный max_score
      try {
        const maxScoreResponse = await leaderboardAPI.getMyMaxScore();
        const userWithUpdatedScore = {
          ...response.data,
          max_score: maxScoreResponse.data.max_score,
        };
        dispatch({ type: 'SET_USER', payload: userWithUpdatedScore });
        console.log('✅ User authenticated successfully');
      } catch (maxScoreError) {
        console.warn('Failed to get max score, using default:', maxScoreError);
        dispatch({ type: 'SET_USER', payload: response.data });
      }
    } catch (error: any) {
      console.log('🔐 User not authenticated:', error.response?.status || error.message);
      dispatch({ type: 'SET_USER', payload: null });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
      checkAuthInProgress.current = false;
    }
  }, []);

  // Проверка авторизации для неавторизованных пользователей
  const checkAuthForUnauthenticated = useCallback(async () => {
    // Если пользователь уже авторизован, не делаем запросы
    if (currentAuthState.current.isAuthenticated && currentAuthState.current.user) {
      return;
    }

    const now = Date.now();

    // Проверяем, не слишком ли часто отправляем запросы /me
    if (now - lastMeRequestTime.current < ME_REQUEST_INTERVAL) {
      return;
    }

    // Проверяем, не идет ли уже проверка
    if (checkAuthInProgress.current) {
      return;
    }

    try {
      checkAuthInProgress.current = true;
      lastMeRequestTime.current = now;

      console.log('🔐 Checking authentication for unauthenticated user...');
      const response = await authAPI.me();

      // Получаем актуальный max_score
      try {
        const maxScoreResponse = await leaderboardAPI.getMyMaxScore();
        const userWithUpdatedScore = {
          ...response.data,
          max_score: maxScoreResponse.data.max_score,
        };
        dispatch({ type: 'SET_USER', payload: userWithUpdatedScore });
        console.log('✅ User authenticated successfully');
      } catch (maxScoreError) {
        console.warn('Failed to get max score, using default:', maxScoreError);
        dispatch({ type: 'SET_USER', payload: response.data });
      }
    } catch (error: any) {
      console.log('🔐 User still not authenticated:', error.response?.status || error.message);
      // Не устанавливаем пользователя в null, так как он уже null
    } finally {
      checkAuthInProgress.current = false;
    }
  }, []);

  // Вход
  const login = async (data: UserLogin) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      await authAPI.login(data);
      await checkAuth(); // Проверяем авторизацию после входа (включая max_score)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Ошибка входа';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Регистрация
  const register = async (data: UserAuth) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      // Регистрируем пользователя
      await authAPI.register(data);

      // Автоматически входим в аккаунт после регистрации
      const loginData: UserLogin = {
        username_or_email: data.username,
        password: data.password,
      };
      await authAPI.login(loginData);

      // Проверяем авторизацию (включая max_score)
      await checkAuth();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Ошибка регистрации';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Выход
  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
      // Сбрасываем состояние проверки авторизации
      checkAuthInProgress.current = false;
      lastCheckTime.current = 0;
      lastMeRequestTime.current = 0;
    }
  };

  // Очистка ошибки
  const clearError = () => {
    dispatch({ type: 'SET_ERROR', payload: null });
  };

  // Обновление max_score пользователя
  const updateUserMaxScore = async () => {
    if (!state.isAuthenticated || !state.user) return;

    try {
      const maxScoreResponse = await leaderboardAPI.getMyMaxScore();
      const updatedUser = {
        ...state.user,
        max_score: maxScoreResponse.data.max_score,
      };
      dispatch({ type: 'SET_USER', payload: updatedUser });
    } catch (error) {
      console.warn('Failed to update max score:', error);
    }
  };

  // Проверяем авторизацию при загрузке приложения
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Периодическая проверка авторизации каждые 0.1 секунды
  useEffect(() => {
    // Очищаем предыдущий интервал
    if (authCheckIntervalRef.current) {
      clearInterval(authCheckIntervalRef.current);
    }

    // Создаем новый интервал
    authCheckIntervalRef.current = setInterval(() => {
      // Проверяем состояние авторизации каждые 0.1 секунды
      if (!currentAuthState.current.isAuthenticated || !currentAuthState.current.user) {
        // Если пользователь не авторизован, пытаемся отправить запрос /me каждые 5 секунд
        checkAuthForUnauthenticated();
      }
    }, AUTH_CHECK_INTERVAL);

    // Очистка при размонтировании
    return () => {
      if (authCheckIntervalRef.current) {
        clearInterval(authCheckIntervalRef.current);
        authCheckIntervalRef.current = null;
      }
    };
  }, [checkAuthForUnauthenticated]);

  // Слушаем события logout из API клиента
  useEffect(() => {
    const handleLogoutEvent = () => {
      console.log('🔐 Logout event received from API client');
      dispatch({ type: 'LOGOUT' });
      // Сбрасываем состояние проверки авторизации
      checkAuthInProgress.current = false;
      lastCheckTime.current = 0;
      lastMeRequestTime.current = 0;
    };

    window.addEventListener('auth:logout', handleLogoutEvent);
    return () => {
      window.removeEventListener('auth:logout', handleLogoutEvent);
    };
  }, []);

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    checkAuth,
    clearError,
    updateUserMaxScore,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Хук для использования контекста
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
