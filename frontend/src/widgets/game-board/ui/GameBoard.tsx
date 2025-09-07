import React, { useRef, useEffect, useCallback } from 'react';
import { GameState, Direction } from '../../../shared/types';
import { GAME_CONFIG, COLORS, FOOD_TYPES, OBSTACLE_TYPES } from '../../../constants/game';
import { useGameLoop } from '../../../shared/lib/hooks/useGameLoop';
import { useInput } from '../../../shared/lib/hooks/useInput';
import {
  moveSnake,
  growSnake,
  checkCollision,
  checkFoodCollision,
  createFood,
  isValidDirection,
  updateGameSpeed,
  calculateScore,
} from '../../../shared/lib/utils/gameEngine';

interface GameBoardProps {
  gameState: GameState;
  onGameStateChange: (newState: GameState) => void;
  onGameOver: (finalScore: number) => void;
}

export const GameBoard: React.FC<GameBoardProps> = ({
  gameState,
  onGameStateChange,
  onGameOver,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const contextRef = useRef<CanvasRenderingContext2D | null>(null);

  // Инициализация Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext('2d');
    if (!context) return;

    contextRef.current = context;

    // Устанавливаем размер canvas
    canvas.width = GAME_CONFIG.canvasWidth;
    canvas.height = GAME_CONFIG.canvasHeight;

    // Настройка контекста
    context.imageSmoothingEnabled = false;
  }, []);

  // Отрисовка игры
  const render = useCallback(() => {
    const context = contextRef.current;
    if (!context) return;

    const { canvas } = context;
    const cellSize = canvas.width / GAME_CONFIG.gridSize;

    // Очистка canvas
    context.fillStyle = COLORS.background;
    context.fillRect(0, 0, canvas.width, canvas.height);

    // Отрисовка сетки
    context.strokeStyle = COLORS.grid;
    context.lineWidth = 0.5;
    for (let i = 0; i <= GAME_CONFIG.gridSize; i++) {
      context.beginPath();
      context.moveTo(i * cellSize, 0);
      context.lineTo(i * cellSize, canvas.height);
      context.stroke();

      context.beginPath();
      context.moveTo(0, i * cellSize);
      context.lineTo(canvas.width, i * cellSize);
      context.stroke();
    }

    // Отрисовка препятствий
    gameState.obstacles.forEach(obstacle => {
      if (obstacle.isActive) {
        const config = OBSTACLE_TYPES[obstacle.type];
        context.fillStyle = config.color;
        context.fillRect(
          obstacle.position.x * cellSize,
          obstacle.position.y * cellSize,
          cellSize,
          cellSize
        );
      }
    });

    // Отрисовка еды
    const foodConfig = FOOD_TYPES[gameState.food.type];
    context.fillStyle = foodConfig.color;
    context.fillRect(
      gameState.food.position.x * cellSize,
      gameState.food.position.y * cellSize,
      cellSize,
      cellSize
    );

    // Отрисовка змейки
    gameState.snake.body.forEach((segment, index) => {
      if (index === 0) {
        // Голова
        context.fillStyle = COLORS.snakeHead;
      } else {
        // Тело
        context.fillStyle = COLORS.snake;
      }

      context.fillRect(
        segment.x * cellSize,
        segment.y * cellSize,
        cellSize,
        cellSize
      );
    });
  }, [gameState]);

  // Обновление игры
  const updateGame = useCallback(() => {
    if (gameState.isGameOver || gameState.isPaused) return;

    // Двигаем змейку
    let newSnake = moveSnake(gameState.snake);

    // Проверяем столкновение с едой
    if (checkFoodCollision(newSnake, gameState.food)) {
      newSnake = growSnake(newSnake);
      const newFood = createFood(newSnake, gameState.obstacles);
      const foodScore = calculateScore(gameState.food.value, 1, gameState.gameSpeed)
      const newScore = gameState.score + foodScore;
      const newSpeed = updateGameSpeed(gameState.gameSpeed, newScore);

      onGameStateChange({
        ...gameState,
        snake: newSnake,
        food: newFood,
        score: newScore,
        gameSpeed: newSpeed,
      });
    } else {
      onGameStateChange({
        ...gameState,
        snake: newSnake,
      });
    }

    // Проверяем столкновения
    if (checkCollision(newSnake, gameState.obstacles, gameState.level)) {
      onGameOver(gameState.score);
    }
  }, [gameState, onGameStateChange, onGameOver]);

  // Обработка ввода
  const handleDirectionChange = useCallback((direction: Direction) => {
    if (isValidDirection(gameState.snake.direction, direction)) {
      onGameStateChange({
        ...gameState,
        snake: {
          ...gameState.snake,
          nextDirection: direction,
        },
      });
    }
  }, [gameState, onGameStateChange]);

  const handlePause = useCallback(() => {
    onGameStateChange({
      ...gameState,
      isPaused: !gameState.isPaused,
    });
  }, [gameState, onGameStateChange]);

  const handleRestart = useCallback(() => {
    // Сброс игры к начальному состоянию
    const newSnake = {
      body: [
        { x: 10, y: 10 },
        { x: 9, y: 10 },
        { x: 8, y: 10 },
      ],
      direction: 'RIGHT' as Direction,
      nextDirection: 'RIGHT' as Direction,
    };

    const newFood = createFood(newSnake, gameState.obstacles);

    onGameStateChange({
      ...gameState,
      snake: newSnake,
      food: newFood,
      score: 0,
      gameSpeed: GAME_CONFIG.initialSpeed,
      isGameOver: false,
      isPaused: false,
    });
  }, [gameState, onGameStateChange]);

  // Используем хуки
  useGameLoop({
    gameState,
    onUpdate: updateGame,
    isPaused: gameState.isPaused,
    isGameOver: gameState.isGameOver,
  });

  useInput({
    onDirectionChange: handleDirectionChange,
    onPause: handlePause,
    onRestart: handleRestart,
    isPaused: gameState.isPaused,
    isGameOver: gameState.isGameOver,
  });

  // Отрисовка при изменении состояния
  useEffect(() => {
    render();
  }, [render]);

  return (
    <div className="text-center">
      <canvas
        ref={canvasRef}
        className="border-2 border-gray-700 rounded-lg max-w-full h-auto"
      />
      <div className="mt-2.5 text-white">
        <div>Счет: {gameState.score}</div>
        <div>Скорость: {Math.round(1000 / gameState.gameSpeed)} FPS</div>
        {gameState.isPaused && <div>ПАУЗА</div>}
        {gameState.isGameOver && <div>ИГРА ОКОНЧЕНА</div>}
      </div>
    </div>
  );
};
