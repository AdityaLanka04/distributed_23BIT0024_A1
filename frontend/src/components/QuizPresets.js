import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function QuizPresets() {
  const [presets, setPresets] = useState([]);
  const [selectedPreset, setSelectedPreset] = useState(null);
  const [username, setUsername] = useState('');
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadPresets();
    
    const handleScroll = () => {
      const reveals = document.querySelectorAll('.fade-in-scroll, .zoom-in-scroll, .section-reveal, .card-reveal');
      reveals.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
          element.classList.add('visible');
        }
      });
    };
    
    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial check
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const loadPresets = async () => {
    try {
      const res = await api.get('/quiz/presets/list');
      setPresets(Object.entries(res.data).map(([id, data]) => ({ id, ...data })));
    } catch (err) {
      console.error('Failed to load presets:', err);
    }
  };

  const handlePresetClick = (preset) => {
    setSelectedPreset(preset);
    setShowModal(true);
  };

  const handleCreateRoom = async () => {
    if (!username) {
      alert('Please enter your username');
      return;
    }

    try {
      const quizRes = await api.post(`/quiz/presets/${selectedPreset.id}`);
      
      const userId = 'user_' + Math.random().toString(36).substr(2, 9);
      const roomRes = await api.post(`/live/create?quiz_id=${quizRes.data.id}&host_id=${userId}&username=${username}&max_players=5`);
      
      sessionStorage.setItem(`userId_${roomRes.data.room_id}`, userId);
      
      alert(`Room created! Room ID: ${roomRes.data.room_id}\nShare this ID with your friends!`);
      navigate(`/live/${roomRes.data.room_id}`);
    } catch (err) {
      console.error(err);
      alert('Failed to create room');
    }
  };

  return (
    <div className="container">
      <div className="section-reveal" style={{ textAlign: 'center', marginBottom: '64px' }}>
        <h1 className="zoom-in-scroll visible" style={{ marginBottom: '16px', color: 'var(--text-primary)' }}>
          Quick Start Quizzes
        </h1>
        <p className="fade-in-scroll visible" style={{ fontSize: '21px', color: 'var(--text-secondary)' }}>
          Choose a category and start a live battle instantly
        </p>
      </div>

      <div className="presets-grid">
        {presets.map((preset, index) => (
          <div
            key={preset.id}
            className="preset-card card-reveal"
            onClick={() => handlePresetClick(preset)}
            style={{
              background: 'white',
              borderRadius: 'var(--radius-lg)',
              padding: '40px',
              cursor: 'pointer',
              transition: 'var(--transition)',
              border: '2px solid var(--border)',
              position: 'relative',
              overflow: 'hidden',
              transitionDelay: `${index * 0.1}s`
            }}
          >
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '6px',
              background: preset.color || 'var(--gradient-primary)'
            }} />
            
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '20px',
              background: `${preset.color}15` || 'rgba(15, 118, 110, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              fontWeight: '800',
              color: preset.color || 'var(--primary)',
              marginBottom: '24px',
              letterSpacing: '-0.5px'
            }}>
              {preset.icon}
            </div>

            <h3 style={{ marginBottom: '12px', fontSize: '24px' }}>
              {preset.title}
            </h3>
            <p style={{ 
              color: 'var(--text-secondary)', 
              marginBottom: '20px',
              lineHeight: '1.6'
            }}>
              {preset.description}
            </p>

            <div style={{
              display: 'flex',
              gap: '16px',
              paddingTop: '20px',
              borderTop: '1px solid var(--border)'
            }}>
              <div style={{
                padding: '8px 16px',
                background: 'var(--bg-secondary)',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '600',
                color: 'var(--text-secondary)'
              }}>
                {preset.category}
              </div>
              <div style={{
                padding: '8px 16px',
                background: 'var(--bg-secondary)',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '600',
                color: 'var(--text-secondary)'
              }}>
                {preset.question_count} Questions
              </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && selectedPreset && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '20px',
              background: selectedPreset.color || 'var(--gradient-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              fontWeight: '800',
              color: 'white',
              margin: '0 auto 32px',
              boxShadow: `0 16px 48px ${selectedPreset.color}40`,
              letterSpacing: '-0.5px'
            }}>
              {selectedPreset.icon}
            </div>
            
            <h3>{selectedPreset.title}</h3>
            <p>{selectedPreset.description}</p>
            
            <div className="form-group">
              <label className="form-label">Your Name</label>
              <input
                type="text"
                placeholder="Enter your name"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            
            <div className="modal-actions">
              <button onClick={() => setShowModal(false)} className="btn btn-secondary">
                Cancel
              </button>
              <button 
                onClick={handleCreateRoom} 
                className="btn"
                style={{
                  background: selectedPreset.color || 'var(--gradient-primary)',
                  boxShadow: `0 8px 24px ${selectedPreset.color}40`
                }}
              >
                Create Room
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default QuizPresets;
