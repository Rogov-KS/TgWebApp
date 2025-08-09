import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
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

  // Проверка авторизации при загрузке
  const checkAuth = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await authAPI.me();

      // Получаем актуальный max_score
      try {
        const maxScoreResponse = await leaderboardAPI.getMyMaxScore();
        const userWithUpdatedScore = {
          ...response.data,
          max_score: maxScoreResponse.data.max_score,
        };
        dispatch({ type: 'SET_USER', payload: userWithUpdatedScore });
      } catch (maxScoreError) {
        console.warn('Failed to get max score, using default:', maxScoreError);
        dispatch({ type: 'SET_USER', payload: response.data });
      }
    } catch (error) {
      console.log('🔐 User not authenticated');
      dispatch({ type: 'SET_USER', payload: null });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

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
        max_score: maxScoreResponse.data,
      };
      dispatch({ type: 'SET_USER', payload: updatedUser });
    } catch (error) {
      console.warn('Failed to update max score:', error);
    }
  };

  // Проверяем авторизацию при загрузке приложения
  useEffect(() => {
    checkAuth();
  }, []);

  // Слушаем события logout из API клиента
  useEffect(() => {
    const handleLogoutEvent = () => {
      dispatch({ type: 'LOGOUT' });
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
