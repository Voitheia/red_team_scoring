#!/bin/bash
echo "This cleanup process KILLS anything using 8000/3000"
fuser -k 8000/tcp
fuser -k 3000/tcp
pkill -f uvicorn
pkill -f react
reset
