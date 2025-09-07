import { Button } from '../../../shared/ui';
import type { Direction } from '../../../shared/types';

interface GameControlsProps {
  onDirectionChange: (direction: Direction) => void;
  onPause: () => void;
  onRestart: () => void;
  isPaused: boolean;
  isGameOver: boolean;
}

export function GameControls({
  onDirectionChange,
  onPause,
  onRestart,
  isPaused,
  isGameOver
}: GameControlsProps) {
  const handleKeyPress = (direction: Direction) => {
    onDirectionChange(direction);
  };

  return (
    <div className="game-controls">
      <div className="game-controls-buttons">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => handleKeyPress('UP')}
          disabled={isGameOver}
        >
          ↑
        </Button>
      </div>

      <div className="game-controls-row">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => handleKeyPress('LEFT')}
          disabled={isGameOver}
        >
          ←
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => handleKeyPress('DOWN')}
          disabled={isGameOver}
        >
          ↓
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => handleKeyPress('RIGHT')}
          disabled={isGameOver}
        >
          →
        </Button>
      </div>

      <div className="game-controls-actions">
        <Button
          variant={isPaused ? 'primary' : 'secondary'}
          size="md"
          onClick={onPause}
          disabled={isGameOver}
        >
          {isPaused ? 'Продолжить' : 'Пауза'}
        </Button>

        <Button
          variant="danger"
          size="md"
          onClick={onRestart}
        >
          Перезапуск
        </Button>
      </div>
    </div>
  );
}
