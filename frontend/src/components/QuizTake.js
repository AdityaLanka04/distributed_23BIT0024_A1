import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

function QuizTake() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);

  useEffect(() => {
    api.get(`/quiz/${id}`)
      .then(res => {
        setQuiz(res.data);
        setAnswers(new Array(res.data.questions.length).fill(-1));
      })
      .catch(err => console.error(err));
  }, [id]);

  const handleAnswer = (answerIndex) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answerIndex;
    setAnswers(newAnswers);
  };

  const handleSubmit = () => {
    api.post('/quiz/submit', {
      quiz_id: id,
      user_id: 'user123',
      answers: answers
    })
    .then(() => navigate('/'))
    .catch(err => console.error(err));
  };

  if (!quiz) return <div className="loading">Loading quiz...</div>;

  const question = quiz.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / quiz.questions.length) * 100;

  return (
    <div className="container">
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div style={{ marginBottom: '48px' }}>
          <h1 style={{ 
            marginBottom: '16px',
            fontSize: '56px',
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text'
          }}>
            {quiz.title}
          </h1>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '16px',
            marginBottom: '24px'
          }}>
            <div className="progress" style={{ margin: 0 }}>
              Question {currentQuestion + 1} of {quiz.questions.length}
            </div>
            <div style={{ 
              flex: 1, 
              height: '8px', 
              background: 'rgba(0, 0, 0, 0.08)', 
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{ 
                height: '100%', 
                width: `${progress}%`,
                background: 'linear-gradient(90deg, #4facfe 0%, #00f2fe 100%)',
                transition: 'width 0.3s ease',
                borderRadius: '4px'
              }} />
            </div>
          </div>
        </div>
        
        <div className="card" style={{ position: 'relative', overflow: 'visible' }}>
          <div style={{
            position: 'absolute',
            top: '-20px',
            left: '40px',
            width: '56px',
            height: '56px',
            borderRadius: '14px',
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '28px',
            fontWeight: '700',
            color: 'white',
            boxShadow: '0 8px 24px rgba(79, 172, 254, 0.4)'
          }}>
            ?
          </div>
          
          <h3 style={{ marginBottom: '40px', marginTop: '24px', fontSize: '28px', lineHeight: '1.4' }}>
            {question.question_text}
          </h3>
          
          <div className="options">
            {question.options.map((option, idx) => (
              <button
                key={idx}
                className={`option-btn ${answers[currentQuestion] === idx ? 'selected' : ''}`}
                onClick={() => handleAnswer(idx)}
                style={{
                  position: 'relative',
                  overflow: 'visible'
                }}
              >
                <span style={{ 
                  display: 'inline-block',
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  background: answers[currentQuestion] === idx 
                    ? 'white' 
                    : 'linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%)',
                  marginRight: '16px',
                  textAlign: 'center',
                  lineHeight: '40px',
                  fontWeight: '800',
                  fontSize: '16px',
                  color: answers[currentQuestion] === idx ? 'var(--primary)' : 'var(--text-secondary)',
                  transition: 'all 0.3s ease',
                  boxShadow: answers[currentQuestion] === idx ? '0 4px 16px rgba(79, 172, 254, 0.3)' : 'none'
                }}>
                  {String.fromCharCode(65 + idx)}
                </span>
                {option}
                {answers[currentQuestion] === idx && (
                  <span style={{
                    position: 'absolute',
                    right: '24px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '16px',
                    fontWeight: '800',
                    color: 'var(--primary)',
                    animation: 'badgePop 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)'
                  }}>
                    ✓
                  </span>
                )}
              </button>
            ))}
          </div>
          
          <div className="navigation">
            {currentQuestion > 0 && (
              <button onClick={() => setCurrentQuestion(currentQuestion - 1)} className="btn-secondary">
                Previous
              </button>
            )}
            <div style={{ flex: 1 }}></div>
            {currentQuestion < quiz.questions.length - 1 ? (
              <button onClick={() => setCurrentQuestion(currentQuestion + 1)} className="btn">
                Next
              </button>
            ) : (
              <button onClick={handleSubmit} className="btn btn-success btn-large">
                Submit Quiz
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default QuizTake;
