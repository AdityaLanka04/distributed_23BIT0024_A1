import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';

function Leaderboard() {
  const { id } = useParams();
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    api.get(`/results/leaderboard/${id}`)
      .then(res => setLeaderboard(res.data.leaderboard))
      .catch(err => console.error(err));
  }, [id]);

  return (
    <div className="container">
      <div className="leaderboard">
        <div style={{ textAlign: 'center', marginBottom: '64px' }}>
          <div style={{
            width: '96px',
            height: '96px',
            borderRadius: '24px',
            background: 'var(--gradient-warm)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '56px',
            fontWeight: '800',
            color: 'white',
            marginBottom: '32px',
            boxShadow: '0 16px 48px rgba(234, 88, 12, 0.4)'
          }}>
            #1
          </div>
          <h1 style={{ 
            marginBottom: '16px',
            color: 'var(--text-primary)'
          }}>
            Leaderboard
          </h1>
          <p style={{ fontSize: '24px' }}>Top performers on this quiz</p>
        </div>
        
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Player</th>
              <th style={{ textAlign: 'right' }}>Score</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((entry, idx) => (
              <tr key={idx} style={{
                background: idx < 3 ? 'linear-gradient(135deg, rgba(250, 112, 154, 0.05) 0%, rgba(254, 225, 64, 0.05) 100%)' : 'transparent'
              }}>
                <td style={{ fontWeight: '700', fontSize: '20px' }}>
                  #{idx + 1}
                </td>
                <td style={{ fontWeight: idx < 3 ? '700' : '500', fontSize: idx === 0 ? '20px' : '18px' }}>
                  {entry[0]}
                </td>
                <td style={{ 
                  fontWeight: '700', 
                  fontSize: idx === 0 ? '24px' : '20px',
                  textAlign: 'right',
                  background: 'var(--gradient-primary)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  {entry[1]}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Leaderboard;
