#!/bin/bash

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate quiz-system

# Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
