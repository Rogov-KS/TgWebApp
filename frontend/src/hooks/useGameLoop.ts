import { useCallback, useRef, useEffect } from 'react';
import { GameState } from '../shared/types';

interface UseGameLoopProps {
  gameState: GameState;
  onUpdate: () => void;
  isPaused: boolean;
  isGameOver: boolean;
}

export const useGameLoop = ({ gameState, onUpdate, isPaused, isGameOver }: UseGameLoopProps) => {
  const animationFrameRef = useRef<number | undefined>(undefined);
  const lastUpdateRef = useRef<number>(0);

  const gameLoop = useCallback((timestamp: number) => {
    if (isPaused || isGameOver) {
      animationFrameRef.current = requestAnimationFrame(gameLoop);
      return;
    }

    if (timestamp - lastUpdateRef.current >= gameState.gameSpeed) {
      onUpdate();
      lastUpdateRef.current = timestamp;
    }

    animationFrameRef.current = requestAnimationFrame(gameLoop);
  }, [gameState.gameSpeed, onUpdate, isPaused, isGameOver]);

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
