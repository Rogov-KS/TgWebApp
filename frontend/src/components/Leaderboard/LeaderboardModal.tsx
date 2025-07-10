import React, { useState, useEffect } from 'react';
import { leaderboardAPI } from '../../api/client';
import type { LeaderboardEntry } from '../../types/auth';
import './LeaderboardModal.css';

interface LeaderboardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function LeaderboardModal({ isOpen, onClose }: LeaderboardModalProps) {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadLeaderboard();
    }
  }, [isOpen]);

  // Обработка клавиши Escape для закрытия модального окна
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

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
    <div className="leaderboard-modal-overlay" onClick={onClose}>
      <div className="leaderboard-modal" onClick={e => e.stopPropagation()}>
        <button className="leaderboard-modal-close" onClick={onClose}>
          ×
        </button>

        <div className="leaderboard-header">
          <h2>🏆 Таблица лидеров</h2>
        </div>

        {isLoading && (
          <div className="leaderboard-loading">
            Загрузка...
          </div>
        )}

        {error && (
          <div className="leaderboard-error">
            {error}
          </div>
        )}

        {!isLoading && !error && (
          <div className="leaderboard-content">
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
                    <div className="leaderboard-score">
                      {entry.max_score}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="leaderboard-footer">
          <button
            className="leaderboard-refresh-btn"
            onClick={loadLeaderboard}
            disabled={isLoading}
          >
            {isLoading ? 'Обновление...' : 'Обновить'}
          </button>
        </div>
      </div>
    </div>
  );
}
