import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar        from './components/Navbar';
import Background   from './components/Background';
import ToastContainer from './components/Toast';
import Home         from './pages/Home';
import Login        from './pages/Login';
import Signup       from './pages/Signup';
import { useToast } from './hooks/useToast';
import { Auth }     from './utils/auth';
import './index.css';

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [user, setUser]       = useState(() => Auth.get());
  const { toasts, showToast, dismiss } = useToast();

  // Ping health on mount
  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(r => r.ok && showToast('API server is online ✓', 'success', 3000))
      .catch(() => {});
  }, []);

  const handleLogin  = (u) => setUser(u);
  const handleLogout = ()  => setUser(null);

  return (
    <BrowserRouter>
      <Background />
      <Navbar user={user} onLogout={handleLogout} />

      <Routes>
        <Route path="/"       element={<Home   showToast={showToast} />} />
        <Route path="/login"  element={user ? <Navigate to="/" replace /> : <Login  onLogin={handleLogin}  showToast={showToast} />} />
        <Route path="/signup" element={user ? <Navigate to="/" replace /> : <Signup onLogin={handleLogin}  showToast={showToast} />} />
        <Route path="*"       element={<Navigate to="/" replace />} />
      </Routes>

      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </BrowserRouter>
  );
}
