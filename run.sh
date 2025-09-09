#!/bin/bash
# do cleanup from old processes
echo "Current set cleanup ports are 3000,8000. This script will KILL processes on these ports."
fuser -k 3000/tcp
fuser -k 8000/tcp
# start new ones
uvicorn fastapi_backend.main:app --reload --port 8000 &
cd react-site; npm start &
