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

  return (
    <div className="user-info">
      <div className="user-info-content">
        <div className="user-avatar">
          {user.first_name.charAt(0).toUpperCase()}
        </div>
        <div className="user-details">
          <div className="user-name">
            {user.first_name} {user.last_name || ''}
          </div>
          <div className="user-username">
            @{user.username}
          </div>
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
