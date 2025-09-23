import type { AxiosResponse } from 'axios';
import type {
  User,
  UserAuth,
  UserLogin,
  LoginResponse,
  LogoutResponse,
  LeaderboardEntry,
  RefreshResponse,
  TelegramAuthResponse,
} from '../types';

function nullResponse<T = any>(): Promise<Pick<AxiosResponse<T>, 'data'>> {
  return Promise.resolve({ data: null as unknown as T });
}

export const authAPI = {
  testPing: (): Promise<Pick<AxiosResponse<string>, 'data'>> => nullResponse<string>(),
  login: (_data: UserLogin): Promise<Pick<AxiosResponse<LoginResponse>, 'data'>> => nullResponse<LoginResponse>(),
  register: (_data: UserAuth): Promise<Pick<AxiosResponse<User>, 'data'>> => nullResponse<User>(),
  logout: (): Promise<Pick<AxiosResponse<LogoutResponse>, 'data'>> => nullResponse<LogoutResponse>(),
  me: (): Promise<Pick<AxiosResponse<User>, 'data'>> => nullResponse<User>(),
  refresh: (): Promise<Pick<AxiosResponse<RefreshResponse>, 'data'>> => nullResponse<RefreshResponse>(),
  telegramAuth: (_initData: string): Promise<Pick<AxiosResponse<TelegramAuthResponse>, 'data'>> => nullResponse<TelegramAuthResponse>(),
};

export const gameAPI = {
  createSession: (_data: { user_id: number; score: number; level: number }): Promise<Pick<AxiosResponse<any>, 'data'>> => nullResponse<any>(),
};

export const leaderboardAPI = {
  getMyMaxScore: (): Promise<Pick<AxiosResponse<number>, 'data'>> => nullResponse<number>(),
  getLeaderboard: (): Promise<Pick<AxiosResponse<LeaderboardEntry[]>, 'data'>> => nullResponse<LeaderboardEntry[]>(),
};

export const googleOAuthAPI = {
  google_url_path: '/oauth2/google',
  getAuthUrl: (): string => '',
  handleCallback: (_code: string, _state: string): Promise<Pick<AxiosResponse<any>, 'data'>> => nullResponse<any>(),
};

export const yandexOAuthAPI = {
  yandex_url_path: '/oauth2/yandex',
  getAuthUrl: (): string => '',
  handleCallback: (_code: string, _state: string): Promise<Pick<AxiosResponse<any>, 'data'>> => nullResponse<any>(),
};
