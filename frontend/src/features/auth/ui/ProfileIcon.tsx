import React, { useState } from 'react';
import { useAuth } from './AuthProvider';
import { useModal, ModalType } from '../../../contexts/ModalContext';
import { AuthModal } from './AuthModal';
import './ProfileIcon.css';

interface ProfileIconProps {
  onGuestPlay: () => void;
}

export function ProfileIcon({ onGuestPlay }: ProfileIconProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const { currentModal, setCurrentModal } = useModal();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleProfileClick = () => {
    if (isAuthenticated) {
      // Если пользователь авторизован, показываем выпадающее меню
      setIsDropdownOpen(!isDropdownOpen);
    } else {
      // Если не авторизован, открываем модальное окно
      setCurrentModal(ModalType.AUTH);
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
    setCurrentModal(ModalType.NONE);
  };

  const handleGuestPlay = () => {
    onGuestPlay();
    setIsDropdownOpen(false);
  };

  // Получаем отображаемое имя пользователя
  const displayName = user?.first_name || user?.username || 'Пользователь';
  const displayInitial = displayName.charAt(0).toUpperCase();
  const displayUsername = user?.username ? `@${user.username}` : '';

  return (
    <div className="profile-icon-container">
      <button
        className="profile-icon-button"
        onClick={handleProfileClick}
        title={isAuthenticated ? 'Профиль' : 'Войти / Зарегистрироваться'}
      >
        {isAuthenticated && user ? (
          <div className="profile-avatar">
            {displayInitial}
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
              {user?.first_name || ''} {user?.last_name || ''}
            </div>
            {displayUsername && (
              <div className="profile-username">
                {displayUsername}
              </div>
            )}
            <div className="profile-score">
              Рекорд: {user?.max_score || 0} очков
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
              onClick={() => setCurrentModal(ModalType.AUTH)}
            >
              Войти в аккаунт
            </button>
          </div>
        </div>
      )}

      {/* Модальное окно авторизации */}
      <AuthModal
        isOpen={currentModal === ModalType.AUTH}
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
