import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HomePage } from './pages/home';
import {
  GoogleAuthCallback,
  YandexAuthCallback,
} from './features/auth/ui/callbacks';
import { AppProviders } from './app/providers';
import { setupTelegramMock } from './shared/lib/telegramMock';
import './App.css';
import { Header } from './widgets/header';
import { Footer } from './widgets/footer';

function App() {
  // Инициализируем Telegram mock окружение если есть параметр ?telegram=true
  setupTelegramMock();
  return (
    <AppProviders>
      <Router>
        <div className="min-h-screen flex flex-col">
          <header>
            <Header />
          </header>

          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/auth/google" element={<GoogleAuthCallback />} />
              <Route path="/auth/yandex" element={<YandexAuthCallback />} />
            </Routes>
          </main>

          <footer>
            <Footer />
          </footer>
        </div>
      </Router>
    </AppProviders>
  );
}

export default App;
