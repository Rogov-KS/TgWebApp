import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { AuthModal } from './AuthModal';
import './ProfileIcon.css';

interface ProfileIconProps {
  onGuestPlay: () => void;
}

export function ProfileIcon({ onGuestPlay }: ProfileIconProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleProfileClick = () => {
    if (isAuthenticated) {
      // Если пользователь авторизован, показываем выпадающее меню
      setIsDropdownOpen(!isDropdownOpen);
    } else {
      // Если не авторизован, открываем модальное окно
      setIsModalOpen(true);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      setIsDropdownOpen(false);
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
  };

  const handleGuestPlay = () => {
    onGuestPlay();
    setIsDropdownOpen(false);
  };

  return (
    <div className="profile-icon-container">
      <button
        className="profile-icon-button"
        onClick={handleProfileClick}
        title={isAuthenticated ? 'Профиль' : 'Войти / Зарегистрироваться'}
      >
        {isAuthenticated && user ? (
          <div className="profile-avatar">
            {user.first_name.charAt(0).toUpperCase()}
          </div>
        ) : (
          <div className="profile-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
        )}
      </button>

      {/* Выпадающее меню для авторизованных пользователей */}
      {isAuthenticated && isDropdownOpen && (
        <div className="profile-dropdown">
          <div className="profile-info">
            <div className="profile-name">
              {user?.first_name} {user?.last_name || ''}
            </div>
            <div className="profile-username">
              @{user?.username}
            </div>
            <div className="profile-score">
              Рекорд: {user?.max_score} очков
            </div>
          </div>
          <div className="profile-actions">
            <button
              className="profile-action-btn logout-btn"
              onClick={handleLogout}
            >
              Выйти
            </button>
          </div>
        </div>
      )}

      {/* Выпадающее меню для гостей */}
      {!isAuthenticated && isDropdownOpen && (
        <div className="profile-dropdown">
          <div className="guest-info">
            <div className="guest-title">Гостевой режим</div>
            <div className="guest-note">
              Результаты не сохраняются в БД
            </div>
          </div>
          <div className="profile-actions">
            <button
              className="profile-action-btn login-btn"
              onClick={() => setIsModalOpen(true)}
            >
              Войти в аккаунт
            </button>
          </div>
        </div>
      )}

      {/* Модальное окно авторизации */}
      <AuthModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onGuestPlay={handleGuestPlay}
      />

      {/* Оверлей для закрытия выпадающего меню */}
      {isDropdownOpen && (
        <div
          className="dropdown-overlay"
          onClick={() => setIsDropdownOpen(false)}
        />
      )}
    </div>
  );
}
