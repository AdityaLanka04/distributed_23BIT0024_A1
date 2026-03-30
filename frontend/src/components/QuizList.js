import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

function QuizList() {
  const [quizzes, setQuizzes] = useState([]);
  const [username, setUsername] = useState('');
  const [showLiveModal, setShowLiveModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [roomId, setRoomId] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/quiz/')
      .then(res => setQuizzes(res.data))
      .catch(err => console.error(err));
    
    const handleScroll = () => {
      const scrolled = window.scrollY;
      const heroSection = document.querySelector('.hero-section');
      const scrollIndicator = document.querySelector('.scroll-indicator');
      
      if (scrollIndicator && scrolled > 100) {
        scrollIndicator.classList.add('hidden');
      } else if (scrollIndicator) {
        scrollIndicator.classList.remove('hidden');
      }
      
      if (heroSection && scrolled > 50) {
        heroSection.classList.add('scrolled');
      } else if (heroSection) {
        heroSection.classList.remove('scrolled');
      }
      
      const reveals = document.querySelectorAll('.fade-in-scroll, .zoom-in-scroll, .slide-in-left, .slide-in-right, .section-reveal, .card-reveal, .stagger-children');
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

  const scrollToQuizzes = () => {
    const quizzesSection = document.querySelector('.quiz-section');
    if (quizzesSection) {
      quizzesSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleCreateLiveRoom = async (quizId) => {
    if (!username) {
      alert('Please enter your username');
      return;
    }

    try {
      const userId = 'user_' + Math.random().toString(36).substr(2, 9);
      const res = await api.post(`/live/create?quiz_id=${quizId}&host_id=${userId}&username=${username}&max_players=5`);
      
      sessionStorage.setItem(`userId_${res.data.room_id}`, userId);
      sessionStorage.setItem(`username_${res.data.room_id}`, username);
      
      alert(`Room created! Room ID: ${res.data.room_id}\nShare this ID with your friends!`);
      
      navigate(`/live/${res.data.room_id}?userId=${encodeURIComponent(userId)}&username=${encodeURIComponent(username)}`);
    } catch (err) {
      console.error(err);
      alert('Failed to create room');
    }
  };

  const handleJoinRoom = async () => {
    if (!username) {
      alert('Please enter your username');
      return;
    }
    if (!roomId) {
      alert('Please enter a room ID');
      return;
    }

    try {
      const userId = 'user_' + Math.random().toString(36).substr(2, 9);
      await api.post('/live/join', {
        room_id: roomId,
        user_id: userId,
        username: username
      });
      
      sessionStorage.setItem(`userId_${roomId}`, userId);
      sessionStorage.setItem(`username_${roomId}`, username);
      
      navigate(`/live/${roomId}?userId=${encodeURIComponent(userId)}&username=${encodeURIComponent(username)}`);
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail;
      alert(detail || 'Failed to join room. Please check the room ID.');
    }
  };

  const openLiveModal = (quiz) => {
    setSelectedQuiz(quiz);
    setShowLiveModal(true);
  };

  const openJoinModal = () => {
    setShowJoinModal(true);
  };

  return (
    <div className="container">
      <div className="hero-section">
        <div className="hero-content">
          <div style={{
            display: 'inline-block',
            padding: '8px 24px',
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
            borderRadius: '24px',
            marginBottom: '32px',
            border: '1px solid rgba(102, 126, 234, 0.2)',
            fontSize: '15px',
            fontWeight: '600',
            color: 'var(--text-secondary)',
            letterSpacing: '0.5px'
          }}>
            QUIZ PLATFORM
          </div>
          <h1 style={{ 
            fontSize: '80px', 
            marginBottom: '24px',
            color: 'var(--text-primary)'
          }}>
            QuizMaster
          </h1>
          <p style={{ 
            fontSize: '28px', 
            marginBottom: '56px',
            color: 'var(--text-secondary)',
            fontWeight: '500',
            maxWidth: '700px',
            margin: '0 auto 56px'
          }}>
            Challenge yourself or compete with friends in real-time battles
          </p>
          <div className="action-buttons" style={{ justifyContent: 'center' }}>
            <button onClick={openJoinModal} className="btn btn-success btn-large" style={{
              boxShadow: '0 12px 40px rgba(52, 199, 89, 0.4)'
            }}>
              Join Room
            </button>
            <Link to="/quiz/create" className="btn btn-large" style={{
              boxShadow: '0 12px 40px rgba(102, 126, 234, 0.4)'
            }}>
              Create Quiz
            </Link>
          </div>
        </div>
      </div>
      
      <div style={{ marginTop: '120px' }}>
        <div style={{ textAlign: 'center', marginBottom: '64px' }}>
          <h2 style={{ 
            fontSize: '48px',
            marginBottom: '16px'
          }}>
            Available Quizzes
          </h2>
          <p style={{ fontSize: '21px', color: 'var(--text-secondary)' }}>
            Choose a quiz and start your journey
          </p>
        </div>
      
        <div className="quiz-grid">
          {quizzes.map((quiz, index) => (
            <div key={quiz.id} className="quiz-card card-reveal">
              <div style={{ 
                width: '72px', 
                height: '72px', 
                borderRadius: '18px',
                background: 'var(--gradient-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '32px',
                fontWeight: '800',
                color: 'white',
                marginBottom: '24px',
                boxShadow: '0 12px 32px rgba(15, 118, 110, 0.4)',
                position: 'relative'
              }}>
                Q
                <div style={{
                  position: 'absolute',
                  top: '-4px',
                  right: '-4px',
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #34c759 0%, #30d158 100%)',
                  border: '3px solid white',
                  fontSize: '12px',
                  fontWeight: '700',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {quiz.questions?.length || 0}
                </div>
              </div>
              <h3>{quiz.title}</h3>
              <p style={{ marginTop: '12px', marginBottom: '20px', lineHeight: '1.6' }}>
                {quiz.description}
              </p>
              
              <div className="quiz-meta">
                <div className="quiz-meta-item">
                  <span style={{ fontWeight: '600', fontSize: '14px' }}>TIME</span>
                  <span>{quiz.duration_minutes} min</span>
                </div>
                <div className="quiz-meta-item">
                  <span style={{ fontWeight: '600' }}>QUESTIONS</span>
                  <span>{quiz.questions?.length || 0}</span>
                </div>
              </div>
              
              <div className="quiz-actions">
                <Link to={`/quiz/${quiz.id}`} className="btn" style={{
                  background: 'var(--gradient-primary)'
                }}>
                  Take Quiz
                </Link>
                <button onClick={() => openLiveModal(quiz)} className="btn btn-live">
                  Live Battle
                </button>
                <Link to={`/leaderboard/${quiz.id}`} className="btn-secondary">
                  Leaderboard
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Room Modal */}
      {showLiveModal && (
        <div className="modal-overlay" onClick={() => setShowLiveModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '20px',
              background: 'linear-gradient(135deg, #ff3b30 0%, #ff2d55 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '40px',
              fontWeight: '800',
              color: 'white',
              margin: '0 auto 32px',
              boxShadow: '0 16px 48px rgba(255, 59, 48, 0.4)'
            }}>
              LIVE
            </div>
            <h3>Start Live Battle</h3>
            <p>Compete with up to 5 players in real-time</p>
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
              <button onClick={() => setShowLiveModal(false)} className="btn-secondary">
                Cancel
              </button>
              <button 
                onClick={() => handleCreateLiveRoom(selectedQuiz.id)} 
                className="btn"
                style={{
                  background: 'var(--gradient-accent)',
                  boxShadow: '0 8px 24px rgba(249, 115, 22, 0.4)'
                }}
              >
                Create Room
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Join Room Modal */}
      {showJoinModal && (
        <div className="modal-overlay" onClick={() => setShowJoinModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '20px',
              background: 'linear-gradient(135deg, #34c759 0%, #30d158 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '40px',
              fontWeight: '800',
              color: 'white',
              margin: '0 auto 32px',
              boxShadow: '0 16px 48px rgba(52, 199, 89, 0.4)'
            }}>
              JOIN
            </div>
            <h3>Join Room</h3>
            <p>Enter the room code shared by your friend</p>
            <div className="form-group">
              <label className="form-label">Your Name</label>
              <input
                type="text"
                placeholder="Enter your name"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Room Code</label>
              <input
                type="text"
                placeholder="e.g., a47398b0"
                value={roomId}
                onChange={(e) => setRoomId(e.target.value.trim())}
                style={{
                  fontFamily: 'monospace',
                  fontSize: '20px',
                  letterSpacing: '2px',
                  textTransform: 'lowercase'
                }}
              />
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowJoinModal(false)} className="btn-secondary">
                Cancel
              </button>
              <button 
                onClick={handleJoinRoom} 
                className="btn"
                style={{
                  background: 'var(--gradient-nature)',
                  boxShadow: '0 8px 24px rgba(5, 150, 105, 0.4)'
                }}
              >
                Join Room
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default QuizList;
