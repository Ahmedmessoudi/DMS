import React, { useEffect, useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import API from './api';
import Login from './components/Login';
import NavBar from './components/NavBar';
import Sidebar from './components/Sidebar';
import DocumentArchive from './components/DocumentArchive';
import Settings from './components/Settings';
import Profile from './components/Profile';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [authError, setAuthError] = useState('');

  // Memoized devBypass configuration
  const devBypass = React.useMemo(() => ({
    enabled: process.env.NODE_ENV === 'development',
    user: {
      id: 1,
      username: 'devadmin',
      role: 'admin',
      email: 'devadmin@example.com'
    },
    token: 'dev-token-placeholder'
  }), []);

  const verifyToken = useCallback(async (token) => {
    try {
      const decoded = jwtDecode(token);
      await API.users.verifyToken();
      setUser(decoded);
      setAuthError('');
    } catch (e) {
      localStorage.removeItem('token');
      setAuthError('Invalid token. Please login again.');
    }
  }, []);

  useEffect(() => {
    if (devBypass.enabled && !localStorage.getItem('token')) {
      localStorage.setItem('token', devBypass.token);
      setUser(devBypass.user);
      return;
    }

    const token = localStorage.getItem('token');
    if (token) {
      verifyToken(token);
    }
  }, [devBypass, verifyToken]);

  const handleLogin = async (loginData) => {
    try {
      const res = await API.users.login(loginData);
      const token = res.data.access_token;
      localStorage.setItem('token', token);
      await verifyToken(token);
    } catch (err) {
      setAuthError(err.response?.data?.msg || 'Login failed. Please try again.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setAuthError('');
  };

  if (!user) {
    return <Login onLogin={handleLogin} error={authError} />;
  }

  return (
    <Router>
      <div className="app-container">
        <NavBar user={user} onLogout={handleLogout} />
        
        <div className="main-content">
          <Sidebar isAdmin={user?.role === 'admin'} userId={user?.id} />
          
          <Routes>
            <Route path="/" element={<DocumentArchive user={user} />} />
            <Route path="/settings" element={<Settings user={user} />} />
            <Route path="/profile" element={<Profile user={user} />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;