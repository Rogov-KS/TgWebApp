import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthProvider';
import { useModal, ModalType } from '../../../contexts/ModalContext';
import { GoogleAuthButton } from './GoogleAuthButton';
import { YandexAuthButton } from './YandexAuthButton';
import { Modal, Input, Button } from '../../../shared/ui';
import type { UserAuth, UserLogin } from '../../../shared/types';
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

  if (!isOpen) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isLogin ? 'Вход' : 'Регистрация'}
      size="md"
    >
      <div className="auth-modal-content">
        <button
          className="auth-mode-toggle"
          onClick={handleModeToggle}
        >
          {isLogin ? 'Создать аккаунт' : 'Уже есть аккаунт?'}
        </button>

        <form onSubmit={handleSubmit} className="auth-form">
          {/* OAuth кнопки */}
          <div className="oauth-buttons">
            <GoogleAuthButton
              onError={(error) => {
                console.error('Google OAuth error:', error);
              }}
            />

            <YandexAuthButton
              onError={(error) => {
                console.error('Yandex OAuth error:', error);
              }}
            />
          </div>

          <div className="auth-divider">
            <span>или</span>
          </div>

          {isLogin ? (
            // Форма входа
            <Input
              label="Username или Email:"
              type="text"
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
          ) : (
            // Форма регистрации
            <>
              <Input
                label="Username:"
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                placeholder="Введите username"
              />

              <Input
                label="Email:"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                placeholder="Введите ваш email"
              />
            </>
          )}

          <Input
            label="Пароль:"
            type="password"
            name="password"
            value={formData.password}
            onChange={handleInputChange}
            required
            placeholder="Введите пароль"
          />

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          <div className="auth-actions">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="auth-submit-btn"
            >
              {isLogin ? 'Войти' : 'Зарегистрироваться'}
            </Button>
          </div>
        </form>

        <div className="auth-guest-section">
          <div className="auth-divider">
            <span>или</span>
          </div>
          <Button
            variant="ghost"
            size="lg"
            onClick={onGuestPlay}
            disabled={isLoading}
            className="auth-guest-btn"
          >
            Играть как гость
          </Button>
          <p className="auth-guest-note">
            Результаты гостевой игры не сохраняются
          </p>
        </div>
      </div>
    </Modal>
  );
}
