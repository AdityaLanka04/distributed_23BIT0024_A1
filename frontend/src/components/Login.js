import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function Login() {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({ username: '', password: '' });

  const handleSubmit = (e) => {
    e.preventDefault();
    api.post('/user/login', credentials)
      .then(() => navigate('/'))
      .catch(err => console.error(err));
  };

  return (
    <div className="container">
      <div className="card" style={{ 
        maxWidth: '540px', 
        margin: '120px auto',
        position: 'relative',
        overflow: 'visible'
      }}>
        <div style={{
          position: 'absolute',
          top: '-48px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '96px',
          height: '96px',
          borderRadius: '24px',
          background: 'var(--gradient-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '48px',
          fontWeight: '700',
          color: 'white',
          boxShadow: '0 16px 48px rgba(15, 118, 110, 0.4)'
        }}>
          Q
        </div>
        
        <h2 style={{ 
          textAlign: 'center', 
          marginBottom: '40px',
          marginTop: '64px',
          color: 'var(--text-primary)'
        }}>
          Welcome Back
        </h2>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              placeholder="Enter your username"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              required
            />
          </div>
          <button type="submit" className="btn btn-large" style={{ width: '100%', marginTop: '24px' }}>
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
