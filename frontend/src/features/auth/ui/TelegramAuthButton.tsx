import { useState } from 'react';
import { useTelegramAuth } from '../../../shared/lib/hooks/useTelegramAuth';
import { useAuth } from './AuthProvider';
import { Button } from '../../../shared/ui';
import './TelegramAuthButton.css';

interface TelegramAuthButtonProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function TelegramAuthButton({
  onSuccess,
  onError,
  variant = 'primary',
  size = 'md',
  className = ''
}: TelegramAuthButtonProps) {
  const { checkTelegramAuth, isTelegramEnvironment } = useTelegramAuth();
  const { checkAuth } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const handleTelegramAuth = async () => {
    if (isLoading) return;

    try {
      setIsLoading(true);
      console.log('🚀 Manual Telegram auth button clicked');

      if (!isTelegramEnvironment()) {
        const errorMsg = 'Приложение не запущено в Telegram. Откройте приложение через Telegram бота.';
        console.warn('⚠️', errorMsg);
        onError?.(errorMsg);
        return;
      }

      const success = await checkTelegramAuth();

      if (success) {
        console.log('✅ Manual Telegram authentication successful');
        // Проверяем данные пользователя после успешной авторизации
        await checkAuth();
        onSuccess?.();
      } else {
        const errorMsg = 'Не удалось авторизоваться через Telegram. Попробуйте еще раз.';
        console.error('❌ Manual Telegram authentication failed');
        onError?.(errorMsg);
      }
    } catch (error: any) {
      const errorMsg = error.message || 'Произошла ошибка при авторизации через Telegram';
      console.error('❌ Telegram auth error:', error);
      onError?.(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      type="button"
      variant={variant}
      size={size}
      onClick={handleTelegramAuth}
      isLoading={isLoading}
      disabled={isLoading}
      className={`telegram-auth-button ${className}`}
    >
      <span className="telegram-auth-button-content">
        <svg
          className="telegram-icon"
          viewBox="0 0 24 24"
          fill="currentColor"
          width="16"
          height="16"
        >
          <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.568 8.16l-1.61 7.59c-.12.54-.44.68-.89.42l-2.46-1.81-1.19 1.15c-.13.13-.24.24-.49.24l.18-2.55 4.59-4.14c.2-.18-.04-.28-.31-.1l-5.68 3.58-2.45-.77c-.53-.16-.54-.53.11-.79l9.57-3.69c.44-.16.83.1.69.79z"/>
        </svg>
        Войти через Telegram
      </span>
    </Button>
  );
}
