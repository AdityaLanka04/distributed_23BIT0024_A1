import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function QuizCreate() {
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState({
    title: '',
    description: '',
    duration_minutes: 30,
    created_by: 'admin',
    questions: []
  });

  const addQuestion = () => {
    setQuiz({
      ...quiz,
      questions: [...quiz.questions, {
        question_text: '',
        options: ['', '', '', ''],
        correct_answer: 0,
        points: 1
      }]
    });
  };

  const updateQuestion = (index, field, value) => {
    const newQuestions = [...quiz.questions];
    newQuestions[index][field] = value;
    setQuiz({ ...quiz, questions: newQuestions });
  };

  const updateOption = (qIndex, oIndex, value) => {
    const newQuestions = [...quiz.questions];
    newQuestions[qIndex].options[oIndex] = value;
    setQuiz({ ...quiz, questions: newQuestions });
  };

  const removeQuestion = (index) => {
    const newQuestions = quiz.questions.filter((_, i) => i !== index);
    setQuiz({ ...quiz, questions: newQuestions });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (quiz.questions.length === 0) {
      alert('Please add at least one question');
      return;
    }
    api.post('/quiz/', quiz)
      .then(() => navigate('/'))
      .catch(err => console.error(err));
  };

  return (
    <div className="container">
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '64px' }}>
          <h1 style={{ 
            marginBottom: '16px',
            color: 'var(--text-primary)'
          }}>
            Create Your Quiz
          </h1>
          <p style={{ fontSize: '24px', color: 'var(--text-secondary)' }}>
            Design your own quiz with custom questions
          </p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="card" style={{ marginBottom: '40px' }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #f97316 0%, #fb923c 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '28px',
              fontWeight: '700',
              color: 'white',
              marginBottom: '32px',
              boxShadow: '0 8px 24px rgba(240, 147, 251, 0.4)'
            }}>
              +
            </div>
            
            <div className="form-group">
              <label className="form-label">Quiz Title</label>
              <input
                type="text"
                placeholder="Give your quiz a catchy title"
                value={quiz.title}
                onChange={(e) => setQuiz({...quiz, title: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                placeholder="What is this quiz about?"
                value={quiz.description}
                onChange={(e) => setQuiz({...quiz, description: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Duration (minutes)</label>
              <input
                type="number"
                placeholder="30"
                value={quiz.duration_minutes || ''}
                onChange={(e) => setQuiz({...quiz, duration_minutes: parseInt(e.target.value) || 0})}
                required
              />
            </div>
          </div>

          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '32px' 
          }}>
            <h2 style={{ margin: 0 }}>
              Questions 
              <span style={{ 
                marginLeft: '12px',
                fontSize: '24px',
                color: 'var(--text-secondary)',
                fontWeight: '600'
              }}>
                ({quiz.questions.length})
              </span>
            </h2>
            <button type="button" onClick={addQuestion} className="btn">
              + Add Question
            </button>
          </div>
        
          {quiz.questions.map((question, qIndex) => (
            <div key={qIndex} className="question-editor">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h4 style={{ margin: 0 }}>Question {qIndex + 1}</h4>
                <button type="button" onClick={() => removeQuestion(qIndex)} className="btn-danger">
                  Remove
                </button>
              </div>
              
              <div className="form-group">
                <label className="form-label">Question</label>
                <input
                  type="text"
                  placeholder="Enter your question"
                  value={question.question_text}
                  onChange={(e) => updateQuestion(qIndex, 'question_text', e.target.value)}
                  required
                />
              </div>
              
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Answer Options (select the correct one)</label>
                <div className="options-editor">
                  {question.options.map((option, oIndex) => (
                    <div key={oIndex} className="option-row">
                      <input
                        type="radio"
                        name={`correct-${qIndex}`}
                        checked={question.correct_answer === oIndex}
                        onChange={() => updateQuestion(qIndex, 'correct_answer', oIndex)}
                      />
                      <input
                        type="text"
                        placeholder={`Option ${oIndex + 1}`}
                        value={option}
                        onChange={(e) => updateOption(qIndex, oIndex, e.target.value)}
                        required
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
          
          <button type="submit" className="btn btn-large" style={{ width: '100%', marginTop: '32px' }}>
            Create Quiz
          </button>
        </form>
      </div>
    </div>
  );
}

export default QuizCreate;
