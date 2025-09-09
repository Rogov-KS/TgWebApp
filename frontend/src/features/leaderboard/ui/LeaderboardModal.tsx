import { useState, useEffect } from 'react';
import { leaderboardAPI } from '../../../shared/api/client';
import { useModal, ModalType } from '../../../shared/lib/contexts/ModalContext';
import { Modal, Button } from '../../../shared/ui';
import type { LeaderboardEntry } from '../../../shared/types';
import './LeaderboardModal.css';

interface LeaderboardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function LeaderboardModal({ isOpen, onClose }: LeaderboardModalProps) {
  const { setCurrentModal } = useModal();
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadLeaderboard();
    }
  }, [isOpen]);

  // Уведомляем контекст о состоянии модального окна
  useEffect(() => {
    setCurrentModal(isOpen ? ModalType.LEADERBOARD : ModalType.NONE);
  }, [isOpen, setCurrentModal]);

  const loadLeaderboard = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await leaderboardAPI.getLeaderboard();
      setLeaderboard(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки таблицы лидеров');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="🏆 Таблица лидеров"
      size="md"
    >
      <div className="leaderboard-content">
        {isLoading && <div className="leaderboard-loading">Загрузка...</div>}

        {error && <div className="leaderboard-error">{error}</div>}

        {!isLoading && !error && (
          <>
            {leaderboard.length === 0 ? (
              <div className="leaderboard-empty">
                Пока нет данных для отображения
              </div>
            ) : (
              <div className="leaderboard-table">
                <div className="leaderboard-header-row">
                  <div className="leaderboard-rank">#</div>
                  <div className="leaderboard-username">Игрок</div>
                  <div className="leaderboard-score">Рекорд</div>
                </div>

                {leaderboard.map((entry) => (
                  <div key={entry.user_id} className="leaderboard-row">
                    <div className="leaderboard-rank" data-place={entry.place}>
                      {entry.place}
                    </div>
                    <div className="leaderboard-username">
                      Игрок #{entry.user_id}
                    </div>
                    <div className="leaderboard-score">{entry.max_score}</div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        <div className="leaderboard-footer">
          <Button
            variant="secondary"
            size="md"
            onClick={loadLeaderboard}
            isLoading={isLoading}
            className="leaderboard-refresh-btn"
          >
            {isLoading ? 'Обновление...' : 'Обновить'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
