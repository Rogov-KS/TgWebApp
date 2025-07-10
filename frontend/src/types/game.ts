export interface Position {
  x: number;
  y: number;
}

export type Direction = 'UP' | 'DOWN' | 'LEFT' | 'RIGHT';

export interface Snake {
  body: Position[];
  direction: Direction;
  nextDirection: Direction;
}

export interface Food {
  position: Position;
  type: FoodType;
  value: number;
}

export type FoodType = 'normal' | 'golden' | 'speed' | 'slow' | 'bonus';

export interface Obstacle {
  position: Position;
  type: ObstacleType;
  isActive: boolean;
}

export type ObstacleType = 'wall' | 'maze' | 'moving' | 'teleport' | 'trap';

export interface Level {
  id: string;
  name: string;
  width: number;
  height: number;
  obstacles: Obstacle[];
  foodTypes: FoodType[];
  speed: number;
  maxScore: number;
  isUnlocked: boolean;
}

export interface GameState {
  snake: Snake;
  food: Food;
  obstacles: Obstacle[];
  score: number;
  level: Level;
  isGameOver: boolean;
  isPaused: boolean;
  gameSpeed: number;
}

export interface GameConfig {
  gridSize: number;
  initialSpeed: number;
  speedIncrement: number;
  maxSpeed: number;
  canvasWidth: number;
  canvasHeight: number;
}
