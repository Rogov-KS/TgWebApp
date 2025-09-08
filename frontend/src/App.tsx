import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HomePage } from './pages/home';
import { GoogleAuthCallback, YandexAuthCallback } from './features/auth/ui/callbacks';
import { AppProviders } from './app/providers';
import './App.css';
import { Header } from './widgets/header';
import { Footer } from './widgets/footer';

function App() {
  return (
    <AppProviders>
      <header>
        <Header />
      </header>

      <Router>
        <main className="App">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/auth/google" element={<GoogleAuthCallback />} />
            <Route path="/auth/yandex" element={<YandexAuthCallback />} />
          </Routes>
        </main>
      </Router>

      <footer>
        <Footer />
      </footer>
    </AppProviders>
  );
}

export default App;