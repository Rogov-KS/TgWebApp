import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useModal, ModalType } from '../../contexts/ModalContext';
import { GoogleAuthButton } from './GoogleAuthButton';
import { YandexAuthButton } from './YandexAuthButton';
import type { UserAuth, UserLogin } from '../../types/auth';
import './AuthModal.css';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGuestPlay: () => void;
}

export function AuthModal({ isOpen, onClose, onGuestPlay }: AuthModalProps) {
  const { login, register, isLoading, error, clearError } = useAuth();
  const { setCurrentModal } = useModal();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState<UserAuth>({
    username: '',
    email: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      if (isLogin) {
        // Для входа используем username_or_email и пароль
        const loginData: UserLogin = {
          username_or_email: formData.username || formData.email,
          password: formData.password,
        };
        await login(loginData);
      } else {
        await register(formData);
      }
      onClose();
    } catch (error) {
      // Ошибка уже обработана в AuthContext
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleModeToggle = () => {
    setIsLogin(!isLogin);
    clearError();
    // При переключении режима очищаем только пароль, остальные поля оставляем
    setFormData(prev => ({
      ...prev,
      password: '',
    }));
  };

  // Уведомляем контекст о состоянии модального окна
  useEffect(() => {
    setCurrentModal(isOpen ? ModalType.AUTH : ModalType.NONE);
  }, [isOpen, setCurrentModal]);

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

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={e => e.stopPropagation()}>
        <button className="auth-modal-close" onClick={onClose}>
          ×
        </button>

        <div className="auth-modal-header">
          <h2>{isLogin ? 'Вход' : 'Регистрация'}</h2>
          <button
            className="auth-mode-toggle"
            onClick={handleModeToggle}
          >
            {isLogin ? 'Создать аккаунт' : 'Уже есть аккаунт?'}
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {/* OAuth кнопки */}
          <div className="oauth-buttons">
            <GoogleAuthButton
              onError={(error) => {
                // Показываем ошибку в существующем error state
                console.error('Google OAuth error:', error);
              }}
            />

            <YandexAuthButton
              onError={(error) => {
                // Показываем ошибку в существующем error state
                console.error('Yandex OAuth error:', error);
              }}
            />
          </div>

          <div className="auth-divider">
            <span>или</span>
          </div>

          {isLogin ? (
            // Форма входа
            <div className="form-group">
              <label htmlFor="username_or_email">Username или Email:</label>
              <input
                type="text"
                id="username_or_email"
                name="username_or_email"
                value={formData.username || formData.email}
                onChange={(e) => {
                  const value = e.target.value;
                  // Определяем, что ввел пользователь - email или username
                  if (value.includes('@')) {
                    setFormData(prev => ({ ...prev, email: value, username: '' }));
                  } else {
                    setFormData(prev => ({ ...prev, username: value, email: '' }));
                  }
                }}
                required
                placeholder="Введите username или email"
              />
            </div>
          ) : (
            // Форма регистрации
            <>
              <div className="form-group">
                <label htmlFor="username">Username:</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                  placeholder="Введите username"
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email:</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  placeholder="Введите ваш email"
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="password">Пароль:</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              placeholder="Введите пароль"
            />
          </div>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          <div className="auth-actions">
            <button
              type="submit"
              className="auth-submit-btn"
              disabled={isLoading}
            >
              {isLoading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться')}
            </button>
          </div>
        </form>

        <div className="auth-guest-section">
          <div className="auth-divider">
            <span>или</span>
          </div>
          <button
            className="auth-guest-btn"
            onClick={onGuestPlay}
            disabled={isLoading}
          >
            Играть как гость
          </button>
          <p className="auth-guest-note">
            Результаты гостевой игры не сохраняются
          </p>
        </div>
      </div>
    </div>
  );
}
