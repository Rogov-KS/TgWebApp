import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HomePage } from './pages/home';
import { GoogleAuthCallback, YandexAuthCallback } from './features/auth/ui/callbacks';
import { AppProviders } from './app/providers';
import './App.css';

function App() {
  return (
    <AppProviders>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/auth/google" element={<GoogleAuthCallback />} />
            <Route path="/auth/yandex" element={<YandexAuthCallback />} />
          </Routes>
        </div>
      </Router>
    </AppProviders>
  );
}

export default App;