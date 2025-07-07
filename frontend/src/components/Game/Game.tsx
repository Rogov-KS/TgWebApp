import React, { useState, useCallback } from 'react';
import { GameState, Level } from '../../types/game';
import { GAME_CONFIG } from '../../constants/game';
import { LEVELS, getLevelById, getNextLevel, unlockLevel } from '../../constants/levels';
import { createSnake, createFood } from '../../utils/gameEngine';
import { SnakeBoard } from './SnakeBoard';
import { useHelloWorld } from '../../api/hooks';

export const Game: React.FC = () => {
  const [currentLevelId, setCurrentLevelId] = useState<string>('level-1');

  // React Query хук для тестового запроса
  const { data: helloWorldData, isLoading, error, refetch } = useHelloWorld();

  const [gameState, setGameState] = useState<GameState>(() => {
    const level = getLevelById('level-1')!;
    const snake = createSnake();
    const food = createFood(snake, level.obstacles);

    return {
      snake,
      food,
      obstacles: level.obstacles,
      score: 0,
      level,
      isGameOver: false,
      isPaused: false,
      gameSpeed: GAME_CONFIG.initialSpeed,
    };
  });

  const handleGameStateChange = useCallback((newState: GameState) => {
    setGameState(newState);
  }, []);

  const handleGameOver = useCallback((finalScore: number) => {
    setGameState(prev => ({
      ...prev,
      isGameOver: true,
      score: finalScore,
    }));

    // Проверяем, нужно ли разблокировать следующий уровень
    const currentLevel = getLevelById(currentLevelId);
    if (currentLevel && finalScore >= currentLevel.maxScore) {
      const nextLevel = getNextLevel(currentLevelId);
      unlockLevel(nextLevel!.id);
    }
  }, [currentLevelId]);

  const handleLevelChange = useCallback((levelId: string) => {
    const level = getLevelById(levelId);
    if (!level || !level.isUnlocked) return;

    const snake = createSnake();
    const food = createFood(snake, level.obstacles);

    setCurrentLevelId(levelId);
    setGameState({
      snake,
      food,
      obstacles: level.obstacles,
      score: 0,
      level,
      isGameOver: false,
      isPaused: false,
      gameSpeed: level.speed,
    });
  }, []);

  const handleRestart = useCallback(() => {
    // Тестовый запрос к API при рестарте игры
    console.log('🔄 Restarting game...');
    refetch().then(() => {
      console.log('✅ API test completed:', helloWorldData);
    }).catch((error) => {
      console.error('❌ API test failed:', error);
    });

    const level = getLevelById(currentLevelId)!;
    const snake = createSnake();
    const food = createFood(snake, level.obstacles);

    setGameState({
      snake,
      food,
      obstacles: level.obstacles,
      score: 0,
      level,
      isGameOver: false,
      isPaused: false,
      gameSpeed: level.speed,
    });
  }, [currentLevelId, refetch, helloWorldData]);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ textAlign: 'center', color: '#FFFFFF', marginBottom: '10px' }}>
          Snake Game
        </h2>

        {/* Выбор уровня */}
        <div style={{
          display: 'flex',
          gap: '10px',
          flexWrap: 'wrap',
          justifyContent: 'center',
          marginBottom: '20px'
        }}>
          {LEVELS.map(level => (
            <button
              key={level.id}
              onClick={() => handleLevelChange(level.id)}
              disabled={!level.isUnlocked}
              style={{
                padding: '8px 16px',
                backgroundColor: level.isUnlocked ? '#4CAF50' : '#666',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: level.isUnlocked ? 'pointer' : 'not-allowed',
                opacity: level.isUnlocked ? 1 : 0.6,
                fontWeight: currentLevelId === level.id ? 'bold' : 'normal',
              }}
            >
              {level.name}
              {!level.isUnlocked && ' 🔒'}
            </button>
          ))}
        </div>

        {/* Информация о текущем уровне */}
        <div style={{
          textAlign: 'center',
          color: '#FFFFFF',
          marginBottom: '20px',
          padding: '10px',
          backgroundColor: '#2a2a2a',
          borderRadius: '8px'
        }}>
          <div>Уровень: {gameState.level.name}</div>
          <div>Цель: {gameState.level.maxScore} очков</div>
          <div>Скорость: {Math.round(1000 / gameState.gameSpeed)} FPS</div>

          {/* Индикатор состояния API */}
          <div style={{
            marginTop: '10px',
            padding: '5px',
            borderRadius: '4px',
            backgroundColor: error ? '#f44336' : isLoading ? '#ff9800' : '#4caf50',
            fontSize: '12px'
          }}>
            API Status: {error ? 'Error' : isLoading ? 'Loading...' : 'Connected'}
            {helloWorldData && <div style={{ fontSize: '10px', opacity: 0.8 }}>Response: {helloWorldData}</div>}
          </div>
        </div>
      </div>

      {/* Игровое поле */}
      <SnakeBoard
        gameState={gameState}
        onGameStateChange={handleGameStateChange}
        onGameOver={handleGameOver}
      />

      {/* Кнопки управления */}
      <div style={{
        textAlign: 'center',
        marginTop: '20px',
        display: 'flex',
        gap: '10px',
        justifyContent: 'center'
      }}>
        <button
          onClick={handleRestart}
          style={{
            padding: '10px 20px',
            backgroundColor: '#FF5722',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px',
          }}
        >
          Начать заново
        </button>

        <button
          onClick={() => setGameState(prev => ({ ...prev, isPaused: !prev.isPaused }))}
          style={{
            padding: '10px 20px',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px',
          }}
        >
          {gameState.isPaused ? 'Продолжить' : 'Пауза'}
        </button>
      </div>

      {/* Инструкции */}
      <div style={{
        marginTop: '30px',
        padding: '15px',
        backgroundColor: '#2a2a2a',
        borderRadius: '8px',
        color: '#CCCCCC'
      }}>
        <h3 style={{ color: '#FFFFFF', marginBottom: '10px' }}>Управление:</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div>
            <strong>Клавиатура:</strong>
            <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
              <li>Стрелки или WASD - движение</li>
              <li>Пробел или P - пауза</li>
              <li>R - рестарт</li>
            </ul>
          </div>
          <div>
            <strong>Мобильные:</strong>
            <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
              <li>Свайпы - движение</li>
              <li>Кнопки на экране</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
