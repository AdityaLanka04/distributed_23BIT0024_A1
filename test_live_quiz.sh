#!/bin/bash

echo "Testing Live Quiz System..."
echo ""


echo "1. Creating a test quiz..."
QUIZ_RESPONSE=$(curl -s -X POST http://localhost:8001/api/quiz/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Quiz",
    "description": "Test",
    "duration_minutes": 5,
    "created_by": "admin",
    "questions": [
      {"question_text": "Q1?", "options": ["A", "B", "C", "D"], "correct_answer": 1, "points": 1},
      {"question_text": "Q2?", "options": ["A", "B", "C", "D"], "correct_answer": 2, "points": 1}
    ]
  }')

QUIZ_ID=$(echo $QUIZ_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Quiz ID: $QUIZ_ID"
echo ""


echo "2. Creating a live room..."
ROOM_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/live/create?quiz_id=$QUIZ_ID&host_id=player1&username=Player1&max_players=5")
ROOM_ID=$(echo $ROOM_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['room_id'])")
echo "Room ID: $ROOM_ID"
echo ""


echo "3. Player 2 joining room..."
curl -s -X POST http://localhost:8001/api/live/join \
  -H "Content-Type: application/json" \
  -d "{\"room_id\":\"$ROOM_ID\",\"user_id\":\"player2\",\"username\":\"Player2\"}" | python3 -m json.tool
echo ""


echo "4. Checking room status..."
curl -s "http://localhost:8001/api/live/room/$ROOM_ID" | python3 -m json.tool
echo ""


echo "5. Player 1 marking ready..."
curl -s -X POST "http://localhost:8001/api/live/ready?room_id=$ROOM_ID&user_id=player1" | python3 -m json.tool
echo ""


echo "6. Player 2 marking ready..."
curl -s -X POST "http://localhost:8001/api/live/ready?room_id=$ROOM_ID&user_id=player2" | python3 -m json.tool
echo ""


echo "7. Final room status..."
curl -s "http://localhost:8001/api/live/room/$ROOM_ID" | python3 -m json.tool
