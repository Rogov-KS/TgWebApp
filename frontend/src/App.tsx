import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Game } from './components/Game/Game';
import { GoogleAuthCallback } from './components/Auth/GoogleAuthCallback';
import { YandexAuthCallback } from './components/Auth/YandexAuthCallback';
import { AuthProvider } from './contexts/AuthContext';
import { ModalProvider } from './contexts/ModalContext';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <ModalProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<Game />} />
              <Route path="/auth/google" element={<GoogleAuthCallback />} />
              <Route path="/auth/yandex" element={<YandexAuthCallback />} />
            </Routes>
          </div>
        </Router>
      </ModalProvider>
    </AuthProvider>
  );
}

export default App;
