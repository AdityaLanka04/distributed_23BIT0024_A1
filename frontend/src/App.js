import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import QuizList from './components/QuizList';
import QuizTake from './components/QuizTake';
import QuizCreate from './components/QuizCreate';
import QuizPresets from './components/QuizPresets';
import Login from './components/Login';
import Leaderboard from './components/Leaderboard';
import LiveQuiz from './components/LiveQuiz';
import './App.css';

function Header() {
  const location = useLocation();
  const isLiveQuiz = location.pathname.startsWith('/live/');
  
  if (isLiveQuiz) return null;
  
  return (
    <header className="App-header">
      <div className="header-content">
        <Link to="/" style={{ textDecoration: 'none' }}>
          <div className="logo">Aditya Lanka 23BIT0024 A1+TA1</div>
        </Link>
        <nav style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <Link to="/" style={{ textDecoration: 'none', color: 'var(--text-primary)', fontSize: '17px' }}>
            Quizzes
          </Link>
          <Link to="/presets" style={{ textDecoration: 'none', color: 'var(--text-primary)', fontSize: '17px' }}>
            Quick Start
          </Link>
          <Link to="/quiz/create" style={{ textDecoration: 'none', color: 'var(--text-primary)', fontSize: '17px' }}>
            Create
          </Link>
        </nav>
      </div>
    </header>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Routes>
          <Route path="/" element={<QuizList />} />
          <Route path="/presets" element={<QuizPresets />} />
          <Route path="/login" element={<Login />} />
          <Route path="/quiz/create" element={<QuizCreate />} />
          <Route path="/quiz/:id" element={<QuizTake />} />
          <Route path="/live/:roomId" element={<LiveQuiz />} />
          <Route path="/leaderboard/:id" element={<Leaderboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
