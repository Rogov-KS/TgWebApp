import axios from 'axios';

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

// Интерцептор для логирования ответов
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url, "response.data: ", response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.config?.url);
    return Promise.reject(error);
  }
);

// API функции
export const authAPI = {
  helloWorld: () => apiClient.get<string>('/auth/hello_world'),
  login: (data: { telegram_id: string; password: string; username?: string; first_name?: string; last_name?: string }) =>
    apiClient.post('/auth/login', data),
  register: (data: { telegram_id: string; password: string; username?: string; first_name?: string; last_name?: string }) =>
    apiClient.post('/auth/register', data),
  logout: () => apiClient.post('/auth/logout'),
  me: () => apiClient.get('/auth/me'),
};