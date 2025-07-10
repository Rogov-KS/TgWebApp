import { Position, Direction, Snake, Food, Obstacle, GameState } from '../types/game';
import { GAME_CONFIG, FOOD_TYPES, INITIAL_SNAKE_POSITION, INITIAL_DIRECTION } from '../constants/game';

export const createSnake = (): Snake => ({
  body: [...INITIAL_SNAKE_POSITION],
  direction: INITIAL_DIRECTION as Direction,
  nextDirection: INITIAL_DIRECTION as Direction,
});

export const createFood = (snake: Snake, obstacles: Obstacle[]): Food => {
  const position = getRandomPosition(snake.body, obstacles);
  const type = getRandomFoodType();

  return {
    position,
    type,
    value: FOOD_TYPES[type].value,
  };
};

export const moveSnake = (snake: Snake): Snake => {
  const newBody = [...snake.body];
  const head = { ...newBody[0] };

  // Обновляем направление
  snake.direction = snake.nextDirection;

  // Двигаем голову
  switch (snake.direction) {
    case 'UP':
      head.y -= 1;
      break;
    case 'DOWN':
      head.y += 1;
      break;
    case 'LEFT':
      head.x -= 1;
      break;
    case 'RIGHT':
      head.x += 1;
      break;
  }

  newBody.unshift(head);
  newBody.pop();

  return {
    ...snake,
    body: newBody,
  };
};

export const growSnake = (snake: Snake): Snake => {
  const newBody = [...snake.body];
  const tail = { ...newBody[newBody.length - 1] };

  newBody.push(tail);

  return {
    ...snake,
    body: newBody,
  };
};

export const isValidDirection = (currentDirection: Direction, newDirection: Direction): boolean => {
  const opposites = {
    UP: 'DOWN',
    DOWN: 'UP',
    LEFT: 'RIGHT',
    RIGHT: 'LEFT',
  };

  return opposites[currentDirection] !== newDirection;
};

export const checkCollision = (
  snake: Snake,
  obstacles: Obstacle[],
  level: { width: number; height: number }
): boolean => {
  const head = snake.body[0];

  // Проверка границ
  if (head.x < 0 || head.x >= level.width || head.y < 0 || head.y >= level.height) {
    return true;
  }

  // Проверка столкновения с собой
  for (let i = 1; i < snake.body.length; i++) {
    if (head.x === snake.body[i].x && head.y === snake.body[i].y) {
      return true;
    }
  }

  // Проверка столкновения с препятствиями
  for (const obstacle of obstacles) {
    if (obstacle.isActive && head.x === obstacle.position.x && head.y === obstacle.position.y) {
      return true;
    }
  }

  return false;
};

export const checkFoodCollision = (snake: Snake, food: Food): boolean => {
  const head = snake.body[0];
  return head.x === food.position.x && head.y === food.position.y;
};

export const getRandomPosition = (snakeBody: Position[], obstacles: Obstacle[]): Position => {
  const occupiedPositions = new Set<string>();

  // Добавляем позиции змейки
  snakeBody.forEach(pos => {
    occupiedPositions.add(`${pos.x},${pos.y}`);
  });

  // Добавляем позиции препятствий
  obstacles.forEach(obstacle => {
    if (obstacle.isActive) {
      occupiedPositions.add(`${obstacle.position.x},${obstacle.position.y}`);
    }
  });

  let position: Position;
  do {
    position = {
      x: Math.floor(Math.random() * GAME_CONFIG.gridSize),
      y: Math.floor(Math.random() * GAME_CONFIG.gridSize),
    };
  } while (occupiedPositions.has(`${position.x},${position.y}`));

  return position;
};

export const getRandomFoodType = (): keyof typeof FOOD_TYPES => {
  const random = Math.random();
  let cumulative = 0;

  for (const [type, config] of Object.entries(FOOD_TYPES)) {
    cumulative += config.probability;
    if (random <= cumulative) {
      return type as keyof typeof FOOD_TYPES;
    }
  }

  return 'normal';
};

export const calculateScore = (baseScore: number, level: number, speed: number): number => {
  const levelMultiplier = 1 + (level - 1) * 0.1;
  const speedMultiplier = 1 + 3 * (GAME_CONFIG.maxSpeed / speed);
  return Math.floor(baseScore * levelMultiplier * speedMultiplier);
};

export const updateGameSpeed = (currentSpeed: number, score: number): number => {
  console.log('in def updateGameSpeed: currentSpeed=', currentSpeed, 'score=', score)
  const newPossibleSpeed = GAME_CONFIG.initialSpeed - Math.floor(score / 100) * GAME_CONFIG.speedIncrement
  console.log('in def updateGameSpeed: newPossibleSpeed=', newPossibleSpeed)
  const newSpeed = Math.max(
    GAME_CONFIG.maxSpeed,
    newPossibleSpeed
  );
  console.log('in def updateGameSpeed: newSpeed=', newSpeed)
  return newSpeed;
};
