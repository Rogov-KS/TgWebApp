import { useCallback, useEffect } from 'react';
import { Direction } from '../shared/types';
import { KEYS } from '../constants/game';
import { useModal } from '../contexts/ModalContext';

interface UseInputProps {
  onDirectionChange: (direction: Direction) => void;
  onPause: () => void;
  onRestart: () => void;
  isPaused: boolean;
  isGameOver: boolean;
}

export const useInput = ({ onDirectionChange, onPause, onRestart, isPaused, isGameOver }: UseInputProps) => {
  const { isAnyModalOpen } = useModal();
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Если открыто модальное окно, не обрабатываем никакие клавиши
    if (isAnyModalOpen) {
      return;
    }

    const key = event.code;

    // Проверяем, является ли клавиша игровой
    const isGameKey = KEYS.UP.includes(key) ||
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
  }, [onDirectionChange, onPause, onRestart, isAnyModalOpen]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  // Обработка свайпов для мобильных устройств
  const handleTouchStart = useCallback((event: TouchEvent) => {
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
  }, [onDirectionChange, isAnyModalOpen]);

  useEffect(() => {
    document.addEventListener('touchstart', handleTouchStart);

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
    };
  }, [handleTouchStart]);
};
