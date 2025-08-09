import axios from 'axios';
import type { User, UserAuth, UserLogin, LoginResponse, LogoutResponse, LeaderboardEntry, RefreshResponse } from '../types/auth';


// Динамический baseURL в зависимости от окружения
const getBaseURL = () => {
  // Используем Vite environment variable

  // Если есть переменная окружения, используем её
  console.log('import.meta.env:', import.meta.env);
  const backendUrl = import.meta.env.VITE_NGROK_BACKEND_URL;
  if (backendUrl && backendUrl !== '') {
    console.log('env.BACKEND_URL:', backendUrl);
    return backendUrl;
  }

  // // Для разработки: если мы не на localhost, используем текущий хост
  // if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
  //   // Предполагаем, что API работает на том же хосте, но на порту 8000
  //   console.log('🚀 window.location.hostname:', `${window.location.protocol}//${window.location.hostname}:8000`);
  //   return `${window.location.protocol}//${window.location.hostname}:8000`;
  // }

  // По умолчанию localhost
  console.log('🚀 default baseURL: http://localhost:8000');
  return 'http://localhost:8000';
};

// Создаем экземпляр axios с базовой конфигурацией
export const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  withCredentials: true, // Для работы с куками
  headers: {
    'Content-Type': 'application/json',
  },
});

// Состояние для управления обновлением токенов
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: any) => void;
  reject: (error: any) => void;
}> = [];

// Функция для обработки очереди неудачных запросов
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });

  failedQueue = [];
};

// Функция для добавления запроса в очередь ожидания
const addToFailedQueue = (originalRequest: any) => {
  console.log('⏳ Token refresh already in progress, adding request to queue:', originalRequest.url);
  return new Promise((resolve, reject) => {
    failedQueue.push({ resolve, reject });
  }).then(() => {
    console.log('✅ Request from queue executed after token refresh:', originalRequest.url);
    return apiClient(originalRequest);
  }).catch((err) => {
    console.error('❌ Request from queue failed after token refresh:', originalRequest.url, err);
    return Promise.reject(err);
  });
};

// Функция для выполнения обновления токена
const performTokenRefresh = async (originalRequest: any) => {
  console.log('🔄 Starting token refresh process...');
  originalRequest._retry = true;
  isRefreshing = true;

  try {
    // Пытаемся обновить токен
    console.log('📡 Sending refresh token request...');
    const refreshResponse = await authAPI.refresh();

    console.log('✅ Token refresh successful, processing queue...');
    // Обрабатываем успешное обновление
    processQueue(null, refreshResponse.data.access_token);

    // Повторяем оригинальный запрос
    console.log('🔄 Retrying original request after token refresh:', originalRequest.url);
    return apiClient(originalRequest);
  } catch (refreshError) {
    console.error('❌ Token refresh failed:', refreshError);
    // Обрабатываем ошибку обновления токена
    processQueue(refreshError, null);

    console.log('🔐 Refresh token failed - triggering logout');

    // Отправляем событие для уведомления AuthContext
    window.dispatchEvent(new CustomEvent('auth:logout'));

    return Promise.reject(refreshError);
  } finally {
    isRefreshing = false;
    console.log('🏁 Token refresh process finished');
  }
};

// Функция для обработки обновления токенов
const handleTokenRefresh = async (originalRequest: any) => {
  console.log('🔍 Handling token refresh for request:', originalRequest.url);

  if (isRefreshing) {
    // Если уже идет обновление токена, добавляем запрос в очередь
    return addToFailedQueue(originalRequest);
  }

  return performTokenRefresh(originalRequest);
};

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
  async (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.config?.url);

    const originalRequest = error.config;

    // Обработка 401 ошибки для автоматического обновления токенов
    // Исключаем запросы на обновление токена, чтобы избежать бесконечного цикла
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/refresh')) {
      console.log('🔐 401 error detected, attempting token refresh...');
      return handleTokenRefresh(originalRequest);
    }

    return Promise.reject(error);
  }
);

// API функции
export const authAPI = {
  helloWorld: () => apiClient.get<string>('/auth/hello_world'),
  login: (data: UserLogin) => apiClient.post<LoginResponse>('/auth/login', data),
  register: (data: UserAuth) => apiClient.post<User>('/auth/register', data),
  logout: () => apiClient.post<LogoutResponse>('/auth/logout'),
  me: () => apiClient.get<User>('/auth/me'),
  refresh: () => apiClient.post<RefreshResponse>('/auth/refresh'),
};

// API для игровых сессий
export const gameAPI = {
  createSession: (data: { user_id: number; score: number; level: number }) =>
    apiClient.post('/game_sessions/', data),
};

// API для лидерборда
export const leaderboardAPI = {
  getMyMaxScore: () => apiClient.get<{ max_score: number }>('/leaderboard/my_max_score'),
  getLeaderboard: () => apiClient.get<LeaderboardEntry[]>('/leaderboard/'),
};

// API для Google OAuth
export const googleOAuthAPI = {
  google_url_path: '/oauth2/google',
  getAuthUrl: () => `${getBaseURL()}${googleOAuthAPI.google_url_path}/url`,
  handleCallback: (code: string, state: string) =>
    apiClient.post(`${googleOAuthAPI.google_url_path}/callback`, { code, state }),
};

// API для Яндекс OAuth
export const yandexOAuthAPI = {
  yandex_url_path: '/oauth2/yandex',
  getAuthUrl: () => `${getBaseURL()}${yandexOAuthAPI.yandex_url_path}/url`,
  handleCallback: (code: string, state: string) =>
    apiClient.post(`${yandexOAuthAPI.yandex_url_path}/callback`, { code, state }),
};
