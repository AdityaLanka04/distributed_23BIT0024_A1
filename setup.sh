#!/bin/bash

echo "Setting up Distributed Quiz Management System..."


if ! command -v conda &> /dev/null; then
    echo "Conda not found. Please install Anaconda or Miniconda first."
    exit 1
fi


echo "Creating conda environment 'quiz-system'..."
conda create -n quiz-system python=3.11 -y


echo "Activating environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate quiz-system


echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt


if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

cd ..


echo "Installing frontend dependencies..."
cd frontend
npm install

cd ..

echo ""
echo "Setup complete!"
echo ""
echo "To start the system:"
echo "1. Start Redis: brew install redis && redis-server"
echo "2. Start backend: conda activate quiz-system && cd backend && uvicorn main:app --reload"
echo "3. Start Celery worker: conda activate quiz-system && cd backend && celery -A distributed.task_queue worker --loglevel=info"
echo "4. Start frontend: cd frontend && npm start"
