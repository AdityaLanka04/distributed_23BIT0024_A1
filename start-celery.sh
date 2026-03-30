#!/bin/bash

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate quiz-system

# Start Celery worker
cd backend
celery -A distributed.task_queue worker --loglevel=info
