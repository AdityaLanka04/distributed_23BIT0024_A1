import { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import api from '../services/api';

function LiveQuiz() {
  const { roomId } = useParams();
  const location = useLocation();
  const [room, setRoom] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [timeLeft, setTimeLeft] = useState(15);
  const [gameStatus, setGameStatus] = useState('waiting');
  const [bonusPoints, setBonusPoints] = useState('');
  const [showBonusInput, setShowBonusInput] = useState(false);
  const queryParamsRef = useRef(new URLSearchParams(location.search));
  
  const userIdRef = useRef(null);
  if (!userIdRef.current) {
    const storageKey = `userId_${roomId}`;
    let storedUserId = sessionStorage.getItem(storageKey) || queryParamsRef.current.get('userId');
    if (!storedUserId) {
      storedUserId = 'user_' + Math.random().toString(36).substring(2, 11);
      sessionStorage.setItem(storageKey, storedUserId);
      console.log('Generated new userId:', storedUserId);
    } else {
      console.log('Retrieved userId from storage:', storedUserId);
      sessionStorage.setItem(storageKey, storedUserId);
    }
    userIdRef.current = storedUserId;
  }
  const userId = userIdRef.current;

  const usernameRef = useRef(null);
  if (!usernameRef.current) {
    const storageKey = `username_${roomId}`;
    const storedUsername = sessionStorage.getItem(storageKey) || queryParamsRef.current.get('username');
    if (storedUsername) {
      sessionStorage.setItem(storageKey, storedUsername);
      usernameRef.current = storedUsername;
    }
  }
  const username = usernameRef.current;
  
  const [wsConnected, setWsConnected] = useState(false);
  const ws = useRef(null);
  const shouldReconnectRef = useRef(true);
  const gameStatusRef = useRef('waiting');
  const messageHandlerRef = useRef(null);
  const lastEventIdRef = useRef(0);

  if (!lastEventIdRef.current) {
    const eventStorageKey = `lastEventId_${roomId}_${userId}`;
    lastEventIdRef.current = parseInt(sessionStorage.getItem(eventStorageKey) || '0', 10);
  }

  const persistLastEventId = useCallback((eventId) => {
    if (!eventId || eventId <= lastEventIdRef.current) return;
    lastEventIdRef.current = eventId;
    sessionStorage.setItem(`lastEventId_${roomId}_${userId}`, String(eventId));
  }, [roomId, userId]);

  const normalizeGameStatus = useCallback((status) => {
    if (status === 'in_progress') return 'playing';
    if (status === 'expired') return 'finished';
    return status || 'waiting';
  }, []);

  const parseServerDate = useCallback((value) => {
    if (!value) return null;
    if (value instanceof Date) return value;
    if (typeof value !== 'string') return new Date(value);

    const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/.test(value);
    return new Date(hasTimezone ? value : `${value}Z`);
  }, []);

  const getTimeLeftFromDeadline = useCallback((deadlineAt) => {
    if (!deadlineAt) return 15;
    const deadline = parseServerDate(deadlineAt);
    if (!deadline || Number.isNaN(deadline.getTime())) return 15;
    const remaining = Math.ceil((deadline.getTime() - Date.now()) / 1000);
    return Math.max(0, remaining);
  }, [parseServerDate]);

  const syncRoomState = useCallback((roomData) => {
    if (!roomData) return;
    const normalizedStatus = normalizeGameStatus(roomData.status);
    setRoom(roomData);
    setGameStatus(normalizedStatus);
    setCurrentQuestion(roomData.current_question_index || 0);
    setTimeLeft(getTimeLeftFromDeadline(roomData.question_deadline_at));

    if (normalizedStatus === 'playing') {
      setSelectedAnswer(null);
    }
  }, [getTimeLeftFromDeadline, normalizeGameStatus]);

  const loadRoom = useCallback(async () => {
    try {
      const res = await api.get(`/live/room/${roomId}`);
      let roomData = res.data;

      const isCurrentUserInRoom = roomData.players?.some((player) => player.user_id === userId);
      if (!isCurrentUserInRoom && username && roomData.status === 'waiting') {
        try {
          await api.post('/live/join', {
            room_id: roomId,
            user_id: userId,
            username
          });
          const joinedRoom = await api.get(`/live/room/${roomId}`);
          roomData = joinedRoom.data;
        } catch (joinErr) {
          console.error('Auto-join failed:', joinErr);
        }
      }

      syncRoomState(roomData);
      
      const quizRes = await api.get(`/quiz/${roomData.quiz_id}`);
      setQuiz(quizRes.data);
    } catch (err) {
      console.error(err);
      alert('Room not found');
    }
  }, [roomId, syncRoomState, userId, username]);

  const handleWebSocketMessage = useCallback((message) => {
    console.log('WebSocket message received:', JSON.stringify(message, null, 2));

    if (message.event_id) {
      if (message.event_id <= lastEventIdRef.current) {
        return;
      }
      persistLastEventId(message.event_id);
    }
    
    switch (message.type) {
      case 'connected':
        console.log('WebSocket connection confirmed by server');
        if (message.data?.room) {
          syncRoomState({
            ...message.data.room,
            status: message.data.status || message.data.room.status
          });
          if (message.data.last_event_id) {
            persistLastEventId(message.data.last_event_id);
          }
        }
        break;
      case 'player_joined':
        console.log('Player joined, reloading room');
        loadRoom();
        break;
      case 'player_reconnected':
        console.log('Player reconnected, reloading room');
        loadRoom();
        break;
      case 'player_ready':
        console.log('Player ready, reloading room');
        if (normalizeGameStatus(message.data?.status) === 'playing') {
          setGameStatus('playing');
          setSelectedAnswer(null);
        }
        loadRoom();
        break;
      case 'game_start':
        console.log('Game starting! Setting status to playing');
        setGameStatus('playing');
        setRoom(prev => prev ? ({
          ...prev,
          status: 'in_progress',
          current_question_index: message.data?.question_index ?? 0,
          question_deadline_at: message.data?.deadline_at ?? prev.question_deadline_at
        }) : prev);
        setTimeLeft(getTimeLeftFromDeadline(message.data?.deadline_at));
        setCurrentQuestion(message.data?.question_index ?? 0);
        setSelectedAnswer(null);
        break;
      case 'answer_submitted':
        console.log('Answer submitted');
        setRoom(prev => ({...prev, players: message.data.players}));
        break;
      case 'question_timeout':
        console.log('Question timed out');
        setRoom(prev => ({...prev, players: message.data.players}));
        break;
      case 'next_question':
        console.log('Next question:', message.data.question_index);
        setGameStatus('playing');
        setRoom(prev => prev ? ({
          ...prev,
          status: 'in_progress',
          current_question_index: message.data.question_index,
          question_deadline_at: message.data?.deadline_at ?? prev.question_deadline_at
        }) : prev);
        setCurrentQuestion(message.data.question_index);
        setSelectedAnswer(null);
        setTimeLeft(getTimeLeftFromDeadline(message.data?.deadline_at));
        break;
      case 'game_end':
        console.log('Game ended, final rankings:', message.data.players);
        setGameStatus('finished');
        setRoom(prev => prev ? ({...prev, status: 'finished', players: message.data.players}) : prev);
        break;
      case 'room_expired':
        console.log('Room expired');
        setGameStatus('finished');
        alert('This room has expired.');
        break;
      case 'player_left':
        console.log('Player left:', message.data.user_id);
        loadRoom();
        break;
      default:
        console.log('Unknown message type:', message.type);
        break;
    }
  }, [getTimeLeftFromDeadline, loadRoom, normalizeGameStatus, persistLastEventId, syncRoomState]);

  useEffect(() => {
    gameStatusRef.current = gameStatus;
  }, [gameStatus]);

  useEffect(() => {
    messageHandlerRef.current = handleWebSocketMessage;
  }, [handleWebSocketMessage]);

  const connectWebSocket = useCallback(() => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }
    
    console.log('Connecting WebSocket...');
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/live/ws/${roomId}/${userId}?last_event_id=${lastEventIdRef.current}`;
    console.log('WebSocket URL:', wsUrl);
    
    ws.current = new WebSocket(wsUrl);
    
    ws.current.onopen = () => {
      console.log('WebSocket connected!');
      setWsConnected(true);
    };
    
    ws.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (messageHandlerRef.current) {
          messageHandlerRef.current(message);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setWsConnected(false);
    };
    
    ws.current.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      setWsConnected(false);
      ws.current = null;
      
      if (shouldReconnectRef.current && event.code !== 1000 && gameStatusRef.current !== 'finished') {
        console.log('Attempting to reconnect in 2 seconds...');
        setTimeout(() => {
          connectWebSocket();
        }, 2000);
      }
    };
  }, [roomId, userId]);

  useEffect(() => {
    shouldReconnectRef.current = true;
    loadRoom();
    connectWebSocket();
    
    return () => {
      shouldReconnectRef.current = false;
      if (ws.current) {
        ws.current.close();
        ws.current = null;
      }
    };
  }, [loadRoom, connectWebSocket]);

  const handleSubmitAnswer = useCallback(async (answer) => {
    if (selectedAnswer !== null) return;
    
    setSelectedAnswer(answer);
    const timeTaken = 15 - timeLeft;
    
    try {
      await api.post('/live/answer', {
        room_id: roomId,
        user_id: userId,
        question_index: currentQuestion,
        answer: answer,
        time_taken: timeTaken
      });
    } catch (err) {
      console.error(err);
      setSelectedAnswer(null);
    }
  }, [selectedAnswer, timeLeft, roomId, userId, currentQuestion]);

  useEffect(() => {
    if (gameStatus === 'playing' && timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && selectedAnswer === null && gameStatus === 'playing') {
      handleSubmitAnswer(-1);
    }
  }, [timeLeft, gameStatus, selectedAnswer, handleSubmitAnswer]);

  const handleReady = async () => {
    if (!wsConnected) {
      alert('Connecting to game server... Please wait.');
      return;
    }
    
    try {
      console.log('Sending ready request...');
      const response = await api.post(`/live/ready?room_id=${roomId}&user_id=${userId}`);
      console.log('Ready response:', response.data);

      const updatedRoom = response.data?.room;
      if (updatedRoom) {
        syncRoomState(updatedRoom);
      }
    } catch (err) {
      console.error('Ready error:', err);
    }
  };

  const copyRoomId = () => {
    navigator.clipboard.writeText(roomId);
    alert('Room ID copied to clipboard!');
  };

  const handleBonusMarks = async () => {
    if (!bonusPoints || isNaN(bonusPoints)) {
      alert('Please enter a valid number');
      return;
    }
    
    try {
      const response = await api.post(`/quiz/bonus_marks/${userId}?bonus_points=${bonusPoints}`);
      alert(`Bonus marks awarded! New total: ${response.data.new_total}`);
      setBonusPoints('');
      setShowBonusInput(false);
    } catch (err) {
      console.error(err);
      alert('Failed to award bonus marks');
    }
  };

  if (!room || !quiz) return <div className="loading">Loading room...</div>;

  const effectiveStatus = normalizeGameStatus(room.status || gameStatus);
  const currentPlayer = room.players?.find((player) => player.user_id === userId);
  const hasAnsweredCurrentQuestion = Boolean(
    currentPlayer?.answered_questions?.includes(currentQuestion)
  );
  const optionsLocked = selectedAnswer !== null || hasAnsweredCurrentQuestion;
  const question = quiz.questions[currentQuestion];

  return (
    <div className="live-quiz">
      <div className="room-header">
        <div className="room-info">
          <h2>Live Battle</h2>
          <div className="room-id-display">
            <span style={{ fontSize: '15px', color: 'var(--text-secondary)' }}>Room Code:</span>
            <span className="room-id-code">{roomId}</span>
            <button onClick={copyRoomId} className="copy-button">Copy</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', alignItems: 'flex-start' }}>
            {!wsConnected && <div className="connection-status" style={{ background: 'linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%)', borderColor: 'rgba(220, 38, 38, 0.2)' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#dc2626' }}></span>
              Connecting...
            </div>}
            {wsConnected && (
              <>
                <div className="connection-status">
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#059669' }}></span>
                  Connected
                </div>
                
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                  {!showBonusInput ? (
                    <button 
                      onClick={() => setShowBonusInput(true)} 
                      className="btn"
                      style={{ 
                        fontSize: '13px', 
                        padding: '8px 16px',
                        background: 'var(--gradient-primary)',
                        color: 'white',
                        border: 'none',
                        cursor: 'pointer'
                      }}
                    >
                      + Bonus Marks
                    </button>
                  ) : (
                    <>
                      <input
                        type="number"
                        value={bonusPoints}
                        onChange={(e) => setBonusPoints(e.target.value)}
                        placeholder="Points"
                        style={{
                          padding: '8px 12px',
                          borderRadius: '8px',
                          border: '1px solid var(--border-color)',
                          background: 'var(--bg-secondary)',
                          color: 'var(--text-primary)',
                          fontSize: '13px',
                          width: '100px'
                        }}
                      />
                      <button 
                        onClick={handleBonusMarks}
                        className="btn"
                        style={{ 
                          fontSize: '13px', 
                          padding: '8px 16px', 
                          background: 'var(--gradient-primary)',
                          color: 'white',
                          border: 'none',
                          cursor: 'pointer'
                        }}
                      >
                        Award
                      </button>
                      <button 
                        onClick={() => {
                          setShowBonusInput(false);
                          setBonusPoints('');
                        }}
                        className="btn"
                        style={{ 
                          fontSize: '13px', 
                          padding: '8px 16px',
                          border: '1px solid var(--border-color)',
                          cursor: 'pointer'
                        }}
                      >
                        Cancel
                      </button>
                    </>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
        {effectiveStatus === 'playing' && (
          <div className="timer">{timeLeft}s</div>
        )}
      </div>

      <div className="live-content">
        {effectiveStatus === 'waiting' && (
          <div className="waiting-room">
            <div style={{
              width: '120px',
              height: '120px',
              borderRadius: '30px',
              background: 'var(--gradient-primary)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '60px',
              fontWeight: '800',
              color: 'white',
              marginBottom: '40px',
              boxShadow: '0 20px 60px rgba(15, 118, 110, 0.4)'
            }}>
              {room.players.length}
            </div>
            <h3>Waiting Room</h3>
            <p>Share the room code with your friends</p>
            <p style={{ fontSize: '15px', color: 'var(--text-secondary)' }}>
              Minimum 2 players required to start
            </p>
            <button 
              onClick={handleReady} 
              className="btn btn-ready"
              disabled={!wsConnected}
              style={{
                boxShadow: wsConnected ? '0 16px 56px rgba(48, 207, 208, 0.5)' : 'none'
              }}
            >
              {wsConnected ? "I'm Ready" : "Connecting..."}
            </button>
          </div>
        )}

        {effectiveStatus === 'playing' && question && (
          <div className="question-container">
            <div className="progress">
              Question {currentQuestion + 1} of {quiz.questions.length}
            </div>
            <p className="question-text">{question.question_text}</p>
            
            <div className="options">
              {question.options.map((option, idx) => (
                <button
                  key={idx}
                  className={`option-btn ${selectedAnswer === idx ? 'selected' : ''}`}
                  onClick={() => handleSubmitAnswer(idx)}
                  disabled={optionsLocked}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        )}

        {effectiveStatus === 'finished' && (
          <div className="game-over">
            <h2>Game Over</h2>
            <div className="final-scores">
              {room.players.map((player, idx) => (
                <div key={idx} className={`final-score ${idx === 0 ? 'winner' : ''}`}>
                  <span>
                    <span style={{ 
                      display: 'inline-block',
                      width: '32px',
                      height: '32px',
                      borderRadius: '8px',
                      background: idx === 0 ? 'linear-gradient(135deg, #ffd700 0%, #ffed4e 100%)' : 
                                  idx === 1 ? 'linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%)' :
                                  idx === 2 ? 'linear-gradient(135deg, #cd7f32 0%, #e8a87c 100%)' :
                                  'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                      marginRight: '12px',
                      textAlign: 'center',
                      lineHeight: '32px',
                      fontWeight: '800',
                      fontSize: '14px',
                      color: idx < 3 ? 'white' : 'var(--text-primary)'
                    }}>
                      {idx + 1}
                    </span>
                    {player.username}
                  </span>
                  <span>{player.score} pts</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="players-sidebar">
          <h3>Players {room.players.length}/{room.max_players}</h3>
          {room.players.map((player, idx) => (
            <div key={idx} className="player-card" style={{
              borderLeft: idx === 0 ? '4px solid #ffd700' : 
                         idx === 1 ? '4px solid #c0c0c0' :
                         idx === 2 ? '4px solid #cd7f32' : '4px solid transparent'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '10px',
                    background: idx === 0 ? 'linear-gradient(135deg, #ffd700 0%, #ffed4e 100%)' :
                               idx === 1 ? 'linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%)' :
                               idx === 2 ? 'linear-gradient(135deg, #cd7f32 0%, #e8a87c 100%)' :
                               'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '14px',
                    fontWeight: '800',
                    color: idx < 3 ? 'white' : 'var(--text-primary)',
                    boxShadow: idx < 3 ? '0 4px 12px rgba(0, 0, 0, 0.2)' : 'none'
                  }}>
                    {idx + 1}
                  </div>
                  <div>
                    <div className="player-name">{player.username}</div>
                    {player.is_ready && effectiveStatus === 'waiting' && (
                      <span className="ready-badge" style={{ marginLeft: 0, marginTop: '4px' }}>Ready</span>
                    )}
                  </div>
                </div>
              </div>
              <span className="score">{player.score}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default LiveQuiz;
