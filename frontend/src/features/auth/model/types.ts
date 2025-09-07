import type { User, UserAuth, UserLogin, AuthState } from '../../../shared/types';

export interface AuthContextType extends AuthState {
  login: (data: UserLogin) => Promise<void>;
  register: (data: UserAuth) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  updateUserMaxScore: () => Promise<void>;
}

export type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'LOGOUT' };
