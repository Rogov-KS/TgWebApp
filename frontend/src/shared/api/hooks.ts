import { useQuery } from '@tanstack/react-query';
import { useCallback, useRef, useEffect, useContext } from 'react';
import { authAPI } from './client';
import { GameState, Direction } from '../types';
import { KEYS } from '../../constants/game';
import { useModal } from '../lib/contexts/ModalContext';
import { AuthContext } from '../lib/contexts/AuthContext';

// API хуки
export const useHelloWorld = () => {
  return useQuery({
    queryKey: ['helloWorld'],
    queryFn: () => authAPI.helloWorld(),
    staleTime: 5 * 60 * 1000, // 5 минут
    retry: 1,
  });
};

// Auth хук
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Game хуки
interface UseGameLoopProps {
  gameState: GameState;
  onUpdate: () => void;
  isPaused: boolean;
  isGameOver: boolean;
}

export const useGameLoop = ({
  gameState,
  onUpdate,
  isPaused,
  isGameOver,
}: UseGameLoopProps) => {
  const animationFrameRef = useRef<number | undefined>(undefined);
  const lastUpdateRef = useRef<number>(0);

  const gameLoop = useCallback(
    (timestamp: number) => {
      if (isPaused || isGameOver) {
        animationFrameRef.current = requestAnimationFrame(gameLoop);
        return;
      }

      if (timestamp - lastUpdateRef.current >= gameState.gameSpeed) {
        onUpdate();
        lastUpdateRef.current = timestamp;
      }

      animationFrameRef.current = requestAnimationFrame(gameLoop);
    },
    [gameState.gameSpeed, onUpdate, isPaused, isGameOver]
  );

  useEffect(() => {
    animationFrameRef.current = requestAnimationFrame(gameLoop);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [gameLoop]);

  const pause = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  }, []);

  const resume = useCallback(() => {
    if (!isPaused && !isGameOver) {
      animationFrameRef.current = requestAnimationFrame(gameLoop);
    }
  }, [gameLoop, isPaused, isGameOver]);

  return { pause, resume };
};

interface UseInputProps {
  onDirectionChange: (direction: Direction) => void;
  onPause: () => void;
  onRestart: () => void;
  isPaused: boolean;
  isGameOver: boolean;
}

export const useInput = ({
  onDirectionChange,
  onPause,
  onRestart,
}: UseInputProps) => {
  const { isAnyModalOpen } = useModal();
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Если открыто модальное окно, не обрабатываем никакие клавиши
      if (isAnyModalOpen) {
        return;
      }

      const key = event.code;

      // Проверяем, является ли клавиша игровой
      const isGameKey =
        KEYS.UP.includes(key) ||
        KEYS.DOWN.includes(key) ||
        KEYS.LEFT.includes(key) ||
        KEYS.RIGHT.includes(key) ||
        KEYS.PAUSE.includes(key) ||
        KEYS.RESTART.includes(key);

      // Если это не игровая клавиша, не обрабатываем её
      if (!isGameKey) {
        return;
      }

      // Направления
      if (KEYS.UP.includes(key)) {
        event.preventDefault();
        onDirectionChange('UP');
      } else if (KEYS.DOWN.includes(key)) {
        event.preventDefault();
        onDirectionChange('DOWN');
      } else if (KEYS.LEFT.includes(key)) {
        event.preventDefault();
        onDirectionChange('LEFT');
      } else if (KEYS.RIGHT.includes(key)) {
        event.preventDefault();
        onDirectionChange('RIGHT');
      }

      // Пауза
      if (KEYS.PAUSE.includes(key)) {
        event.preventDefault();
        onPause();
      }

      // Рестарт
      if (KEYS.RESTART.includes(key)) {
        event.preventDefault();
        onRestart();
      }
    },
    [onDirectionChange, onPause, onRestart, isAnyModalOpen]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  // Обработка свайпов для мобильных устройств
  const handleTouchStart = useCallback(
    (event: TouchEvent) => {
      // Если открыто модальное окно, не обрабатываем свайпы
      if (isAnyModalOpen) {
        return;
      }

      const touch = event.touches[0];
      const startX = touch.clientX;
      const startY = touch.clientY;

      const handleTouchEnd = (event: TouchEvent) => {
        const touch = event.changedTouches[0];
        const endX = touch.clientX;
        const endY = touch.clientY;

        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const minSwipeDistance = 30;

        if (Math.abs(deltaX) > Math.abs(deltaY)) {
          // Горизонтальный свайп
          if (Math.abs(deltaX) > minSwipeDistance) {
            if (deltaX > 0) {
              onDirectionChange('RIGHT');
            } else {
              onDirectionChange('LEFT');
            }
          }
        } else {
          // Вертикальный свайп
          if (Math.abs(deltaY) > minSwipeDistance) {
            if (deltaY > 0) {
              onDirectionChange('DOWN');
            } else {
              onDirectionChange('UP');
            }
          }
        }

        document.removeEventListener('touchend', handleTouchEnd);
      };

      document.addEventListener('touchend', handleTouchEnd);
    },
    [onDirectionChange, isAnyModalOpen]
  );

  useEffect(() => {
    document.addEventListener('touchstart', handleTouchStart);

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
    };
  }, [handleTouchStart]);
};
