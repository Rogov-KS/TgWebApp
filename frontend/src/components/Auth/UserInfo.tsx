import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './UserInfo.css';

export function UserInfo() {
  const { user, logout, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="user-info">
        <div className="user-info-loading">Загрузка...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  // Получаем отображаемое имя пользователя
  const displayName = user.first_name || user.username || 'Пользователь';
  const displayInitial = displayName.charAt(0).toUpperCase();
  const displayUsername = user.username ? `@${user.username}` : '';

  return (
    <div className="user-info">
      <div className="user-info-content">
        <div className="user-avatar">
          {displayInitial}
        </div>
        <div className="user-details">
          <div className="user-name">
            {user.first_name || ''} {user.last_name || ''}
          </div>
          {displayUsername && (
            <div className="user-username">
              {displayUsername}
            </div>
          )}
          <div className="user-score">
            Лучший результат: {user.max_score}
          </div>
        </div>
        <button
          className="user-logout-btn"
          onClick={handleLogout}
          disabled={isLoading}
        >
          Выйти
        </button>
      </div>
    </div>
  );
}
