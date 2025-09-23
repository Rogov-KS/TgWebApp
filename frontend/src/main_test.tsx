import { StrictMode, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { initApp } from './app/initApp';
import { GetTgInitData, IsInTMA } from './shared/lib/utils/tg_helper/telegram_wrapper';
import { authAPI } from './shared/api/export_client';

const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('Failed to find the root element');

function TestApp() {
  // Инициализируем приложение
  initApp();

  const [ping, setPing] = useState<string | null>(null);
  const [pingError, setPingError] = useState<string | null>(null);

  useEffect(() => {
    authAPI
      .testPing()
      .then((res) => {
        console.log('res:', res);
        const value = typeof res.data === 'string' ? res.data : JSON.stringify(res.data);
        setPing(value);
      })
      .catch((err) => {
        console.log('err:', err);
        setPingError(err?.message ?? 'Unknown error');
      });
  }, []);

  return (
    <div>
      <p>Hello world!</p>
      <h1>Is in TMA: {IsInTMA() ? 'Yes' : 'No'}</h1>
      <h2>GetTgInitData: {GetTgInitData() || 'null'}</h2>
      <h3>/test/ping: {pingError ? `error: ${pingError}` : ping ?? 'loading...'}</h3>
      <h3>window.location.search: {window.location.search}</h3>
    </div>
  );
}

createRoot(rootElement).render(
  <StrictMode>
    <TestApp />
  </StrictMode>
);
