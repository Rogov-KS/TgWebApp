export interface User {
  id: number;
  telegram_id: number;
  hashed_password: string;
  username: string | null;
  first_name: string;
  last_name: string | null;
  language_code: string | null;
  is_bot: boolean;
  is_active: boolean;
  max_score: number;
  created_at: string;
  updated_at: string | null;
}

export interface UserAuth {
  telegram_id: number;
  username: string;
  password: string;
  first_name: string;
  last_name: string | null;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface LogoutResponse {
  message: string;
}
