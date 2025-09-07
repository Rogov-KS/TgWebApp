export interface User {
  id: number;
  telegram_id: number | null;
  email: string | null;
  username: string | null;
  hashed_password: string;
  first_name: string | null;
  last_name: string | null;
  language_code: string | null;
  is_bot: boolean;
  is_active: boolean;
  max_score: number;
  created_at: string;
  updated_at: string | null;
}

export interface UserAuth {
  username: string;
  email: string;
  password: string;
}

export interface UserLogin {
  username_or_email: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LogoutResponse {
  message: string;
}

export interface LeaderboardEntry {
  user_id: number;
  max_score: number;
  place: number;
}
