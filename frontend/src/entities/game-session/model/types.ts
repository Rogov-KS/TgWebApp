export interface GameSession {
  id: number;
  user_id: number;
  score: number;
  level: number;
  created_at: string;
}

export interface CreateGameSessionRequest {
  user_id: number;
  score: number;
  level: number;
}

export interface GameSessionState {
  currentSession: GameSession | null;
  isLoading: boolean;
  error: string | null;
}
