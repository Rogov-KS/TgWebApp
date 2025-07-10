import { GameConfig, FoodType, ObstacleType } from '../types/game';

export const GAME_CONFIG: GameConfig = {
  gridSize: 20,
  initialSpeed: 150,
  speedIncrement: 5,
  maxSpeed: 50,
  canvasWidth: 400,
  canvasHeight: 400,
};

export const FOOD_TYPES: Record<FoodType, { value: number; color: string; probability: number }> = {
  normal: { value: 10, color: '#4CAF50', probability: 0.7 },
  golden: { value: 50, color: '#FFD700', probability: 0.15 },
  speed: { value: 20, color: '#FF5722', probability: 0.1 },
  slow: { value: 15, color: '#9C27B0', probability: 0.03 },
  bonus: { value: 100, color: '#E91E63', probability: 0.02 },
};

export const OBSTACLE_TYPES: Record<ObstacleType, { color: string; isSolid: boolean }> = {
  wall: { color: '#795548', isSolid: true },
  maze: { color: '#607D8B', isSolid: true },
  moving: { color: '#FF9800', isSolid: true },
  teleport: { color: '#00BCD4', isSolid: false },
  trap: { color: '#F44336', isSolid: true },
};

export const COLORS = {
  background: '#1a1a1a',
  grid: '#2a2a2a',
  snake: '#4CAF50',
  snakeHead: '#66BB6A',
  border: '#333333',
  text: '#FFFFFF',
  textSecondary: '#CCCCCC',
};

export const KEYS = {
  UP: ['ArrowUp', 'KeyW'],
  DOWN: ['ArrowDown', 'KeyS'],
  LEFT: ['ArrowLeft', 'KeyA'],
  RIGHT: ['ArrowRight', 'KeyD'],
  PAUSE: ['Space', 'KeyP'],
  RESTART: ['KeyR'],
};

export const INITIAL_SNAKE_POSITION = [
  { x: 10, y: 10 },
  { x: 9, y: 10 },
  { x: 8, y: 10 },
];

export const INITIAL_DIRECTION = 'RIGHT';
