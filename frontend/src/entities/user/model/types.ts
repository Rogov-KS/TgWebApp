import type { AuthState } from '../../../shared/types';

export interface UserState extends AuthState {
  // Дополнительные поля для user entity если нужны
}

export interface UserProfile {
  id: number;
  username: string | null;
  email: string | null;
  maxScore: number;
  createdAt: string;
}
