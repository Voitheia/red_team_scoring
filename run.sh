#!/bin/bash
# do cleanup from old processes
echo "Current set cleanup ports are 5173,3000. This script will KILL processes on these ports."
fuser -k 3000/tcp
fuser -k 5173/tcp
# start new ones
uvicorn fastapi_backend.main:app --reload --port 3000 &
cd react; npm run dev &
