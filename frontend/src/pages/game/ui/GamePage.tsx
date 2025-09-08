import { useState, useCallback } from 'react';
import { GameState } from '../../../shared/types';
import { GAME_CONFIG } from '../../../constants/game';
import { LEVELS, getLevelById, getNextLevel, unlockLevel } from '../../../constants/levels';
import { createSnake, createFood } from '../../../shared/lib/utils/gameEngine';
import { GameBoard } from '../../../widgets/game-board';
import { useHelloWorld } from '../../../shared/api/hooks';
import { useAuth } from '../../../features/auth';
import { gameAPI } from '../../../shared/api/client';
import { Button } from '../../../shared/ui';

export const GamePage: React.FC = () => {
  const [currentLevelId, setCurrentLevelId] = useState<string>('level-1');
  const [isGuestMode] = useState(false);
  const [guestBestScore, setGuestBestScore] = useState(() => {
    return parseInt(localStorage.getItem('guestBestScore') || '0');
  });

  // React Query хук для тестового запроса
  const { data: helloWorldData, isLoading, error, refetch } = useHelloWorld();

  // Auth context
  const { user, isAuthenticated, updateUserMaxScore } = useAuth();

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

  const handleGameOver = useCallback(async (finalScore: number) => {
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

    // Сохраняем результат
    if (isAuthenticated && user) {
      try {
        // Сохраняем в БД для авторизованных пользователей
        await gameAPI.createSession({
          user_id: user.id,
          score: finalScore,
          level: parseInt(currentLevelId.replace('level-', '')),
        });
        console.log('✅ Game session saved to database');

        // Обновляем max_score пользователя
        await updateUserMaxScore();
        console.log('✅ User max score updated');
      } catch (error) {
        console.error('❌ Failed to save game session:', error);
      }
    } else if (isGuestMode) {
      // Сохраняем локально для гостей
      if (finalScore > guestBestScore) {
        setGuestBestScore(finalScore);
        localStorage.setItem('guestBestScore', finalScore.toString());
        console.log('✅ Guest best score updated:', finalScore);
      }
    }
  }, [currentLevelId, isAuthenticated, user, isGuestMode, guestBestScore]);

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
    <div className="p-5 max-w-4xl mx-auto">

      {/* Индикатор режима игры */}
      {isGuestMode && (
        <div className="bg-orange-500 text-white px-4 py-2 rounded-lg mb-4 text-center text-sm">
          🎮 Гостевой режим - результаты не сохраняются в БД
          <br />
          Лучший результат: {guestBestScore} очков
        </div>
      )}

      <div className="mb-5">
        {/* Выбор уровня */}
        <div className="flex gap-2.5 flex-wrap justify-center mb-5">
          {LEVELS.map(level => (
            <Button
              key={level.id}
              variant={level.isUnlocked ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => handleLevelChange(level.id)}
              disabled={!level.isUnlocked}
              className={currentLevelId === level.id ? 'font-bold' : ''}
            >
              {level.name}
              {!level.isUnlocked && ' 🔒'}
            </Button>
          ))}
        </div>

        {/* Информация о текущем уровне */}
        <div className="text-center text-white mb-5 p-2.5 bg-gray-800 dark:bg-gray-900 rounded-lg border border-gray-700 dark:border-gray-600">
          <div>Уровень: {gameState.level.name}</div>
          <div>Цель: {gameState.level.maxScore} очков</div>
          <div>Скорость: {Math.round(1000 / gameState.gameSpeed)} FPS</div>

          {/* Информация о рекордах */}
          {isAuthenticated && user && (
            <div className="mt-2 text-green-500">
              Ваш рекорд: {user.max_score} очков
            </div>
          )}

          {/* Индикатор состояния API */}
          <div className={`mt-2.5 p-1.5 rounded text-xs ${
            error ? 'bg-red-500' : isLoading ? 'bg-orange-500' : 'bg-green-500'
          }`}>
            API Status: {error ? 'Error' : isLoading ? 'Loading...' : 'Connected'}
            {helloWorldData && <div className="text-xs opacity-80">Response: {helloWorldData.data}</div>}
          </div>
        </div>
      </div>

      {/* Игровое поле */}
      <GameBoard
        gameState={gameState}
        onGameStateChange={handleGameStateChange}
        onGameOver={handleGameOver}
      />

      {/* Кнопки управления */}
      <div className="text-center mt-5 flex gap-2.5 justify-center">
        <Button
          variant="danger"
          size="md"
          onClick={handleRestart}
        >
          Начать заново
        </Button>

        <Button
          variant={gameState.isPaused ? 'primary' : 'secondary'}
          size="md"
          onClick={() => setGameState(prev => ({ ...prev, isPaused: !prev.isPaused }))}
        >
          {gameState.isPaused ? 'Продолжить' : 'Пауза'}
        </Button>
      </div>

      {/* Инструкции */}
      <div className="mt-8 p-4 bg-gray-800 dark:bg-gray-900 rounded-lg text-gray-300 dark:text-gray-400 border border-gray-700 dark:border-gray-600">
        <h3 className="text-white mb-2.5">Управление:</h3>
        <div className="grid grid-cols-2 gap-2.5">
          <div>
            <strong>Клавиатура:</strong>
            <ul className="my-1 pl-5">
              <li>Стрелки или WASD - движение</li>
              <li>Пробел или P - пауза</li>
              <li>R - рестарт</li>
            </ul>
          </div>
          <div>
            <strong>Мобильные:</strong>
            <ul className="my-1 pl-5">
              <li>Свайпы - движение</li>
              <li>Кнопки на экране</li>
            </ul>
          </div>
        </div>
      </div>

    </div>
  );
};
