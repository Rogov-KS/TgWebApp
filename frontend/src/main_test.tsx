import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import { initApp } from './app/initApp';
import { GetTgInitData, IsInTMA } from './shared/lib/utils/tg_helper/telegram_wrapper';

const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('Failed to find the root element');

function TestApp() {
  // Инициализируем приложение
  initApp();

  return (
    <div>
      <p>Hello world!</p>
      <h1>Is in TMA: {IsInTMA() ? 'Yes' : 'No'}</h1>
      <h2>GetTgInitData: {GetTgInitData() || 'null'}</h2>
    </div>
  );
}

createRoot(rootElement).render(
  <StrictMode>
    <TestApp />
  </StrictMode>
);
