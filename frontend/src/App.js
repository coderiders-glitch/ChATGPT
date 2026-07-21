import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Login from './components/Login';
import { getCurrentUser, logout } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (error) {
        console.error('Auth check failed:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    await logout();
    setUser(null);
  };

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="App">
      {user ? (
        <>
          <header className="app-header">
            <h1>Managed Container Service</h1>
            <div className="user-info">
              <span>Welcome, {user.username || 'User'}</span>
              <button onClick={handleLogout}>Logout</button>
            </div>
          </header>
          <main>
            <ChatInterface />
          </main>
        </>
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;