import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useModal, ModalType } from '../../contexts/ModalContext';
import type { UserAuth } from '../../types/auth';
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
    telegram_id: 0,
    username: '',
    password: '',
    first_name: '',
    last_name: null,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      if (isLogin) {
        // Для входа используем только telegram_id и пароль
        const loginData = {
          telegram_id: formData.telegram_id,
          password: formData.password,
          username: '', // Пустые значения для обязательных полей
          first_name: '',
          last_name: null,
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
      [name]: name === 'telegram_id' ? parseInt(value) || 0 : value,
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
          <div className="form-group">
            <label htmlFor="telegram_id">Telegram ID:</label>
            <input
              type="number"
              id="telegram_id"
              name="telegram_id"
              value={formData.telegram_id || ''}
              onChange={handleInputChange}
              required
              placeholder="Введите ваш Telegram ID"
            />
          </div>

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

          {/* Дополнительные поля только для регистрации */}
          {!isLogin && (
            <>
              <div className="form-group">
                <label htmlFor="username">Имя пользователя:</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                  placeholder="Введите имя пользователя"
                />
              </div>

              <div className="form-group">
                <label htmlFor="first_name">Имя:</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                  placeholder="Введите ваше имя"
                />
              </div>

              <div className="form-group">
                <label htmlFor="last_name">Фамилия (необязательно):</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name || ''}
                  onChange={handleInputChange}
                  placeholder="Введите вашу фамилию"
                />
              </div>
            </>
          )}

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
