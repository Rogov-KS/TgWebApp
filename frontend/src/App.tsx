import React from 'react';
import { Game } from './components/Game/Game';
import { AuthProvider } from './contexts/AuthContext';
import { ModalProvider } from './contexts/ModalContext';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <ModalProvider>
        <div className="App">
          <Game />
        </div>
      </ModalProvider>
    </AuthProvider>
  );
}

export default App;
