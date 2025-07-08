import axios from 'axios';
import type { User, UserAuth, LoginResponse, LogoutResponse } from '../types/auth';

// Создаем экземпляр axios с базовой конфигурацией
export const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  withCredentials: true, // Для работы с куками
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для логирования запросов
apiClient.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Интерцептор для логирования ответов и обработки ошибок авторизации
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url, "response.data: ", response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.config?.url);

    // Обработка 401 ошибки для автоматического logout
    if (error.response?.status === 401) {
      console.log('🔐 Unauthorized - triggering logout');
      // Удаляем cookie вручную, так как AuthContext может быть недоступен
      document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      // Можно также отправить событие для уведомления AuthContext
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }

    return Promise.reject(error);
  }
);

// API функции
export const authAPI = {
  helloWorld: () => apiClient.get<string>('/auth/hello_world'),
  login: (data: UserAuth) => apiClient.post<LoginResponse>('/auth/login', data),
  register: (data: UserAuth) => apiClient.post<User>('/auth/register', data),
  logout: () => apiClient.post<LogoutResponse>('/auth/logout'),
  me: () => apiClient.get<User>('/auth/me'),
};

// API для игровых сессий
export const gameAPI = {
  createSession: (data: { user_id: number; score: number; level: number }) =>
    apiClient.post('/game_sessions/', data),
};

// API для лидерборда
export const leaderboardAPI = {
  getMyMaxScore: () => apiClient.get<{ max_score: number }>('/leaderboard/my_max_score'),
};
