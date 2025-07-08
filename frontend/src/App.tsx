import React from 'react';
import { Game } from './components/Game/Game';
import { AuthProvider } from './contexts/AuthContext';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Game />
      </div>
    </AuthProvider>
  );
}

export default App;
