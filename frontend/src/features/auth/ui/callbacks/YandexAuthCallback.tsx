import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { yandexOAuthAPI } from '../../../../shared/api/client';
import { useAuth } from '../../../../shared/api/hooks';
import './YandexAuthCallback.css';

export function YandexAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const {} = useAuth();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>(
    'loading'
  );
  const [errorMessage, setErrorMessage] = useState<string>('');
  const hasProcessedRef = useRef(false);

  useEffect(() => {
    const handleCallback = async () => {
      // Защита от повторных запросов
      if (hasProcessedRef.current) {
        return;
      }
      hasProcessedRef.current = true;

      try {
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');

        if (error) {
          setStatus('error');
          setErrorMessage('Ошибка авторизации через Яндекс');
          return;
        }

        if (!code || !state) {
          setStatus('error');
          setErrorMessage('Отсутствуют необходимые параметры авторизации');
          return;
        }

        // Отправляем параметры на бекенд
        const response = await yandexOAuthAPI.handleCallback(code, state);

        console.log('Яндекс OAuth callback response:', response.data);

        // Если авторизация успешна, перенаправляем на главную страницу
        setStatus('success');

        // Небольшая задержка для показа сообщения об успехе
        setTimeout(() => {
          navigate('/', { replace: true });
        }, 2000);
      } catch (error) {
        console.error('Ошибка при обработке Яндекс OAuth callback:', error);
        setStatus('error');
        setErrorMessage('Ошибка при завершении авторизации');
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="yandex-callback-container">
      <div className="yandex-callback-content">
        {status === 'loading' && (
          <>
            <div className="loading-spinner"></div>
            <h2>Завершение авторизации...</h2>
            <p>Пожалуйста, подождите</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="success-icon">✓</div>
            <h2>Авторизация успешна!</h2>
            <p>Перенаправление на главную страницу...</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="error-icon">✗</div>
            <h2>Ошибка авторизации</h2>
            <p>{errorMessage}</p>
            <button
              className="retry-btn"
              onClick={() => navigate('/', { replace: true })}
            >
              Вернуться на главную
            </button>
          </>
        )}
      </div>
    </div>
  );
}
