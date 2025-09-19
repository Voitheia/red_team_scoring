#!/bin/bash

# Linux Test IOC Deploy Script
# Deploys a test IOC (malicious file) to the home directory
# Returns JSON with deployment status

# Define the IOC file to create
IOC_FILE="$HOME/.hidden_malware.txt"

# Function to output JSON
output_json() {
    local status=$1
    local message=$2
    local details=$3

    echo "{\"status\": $status, \"message\": \"$message\", \"details\": \"$details\", \"file\": \"$IOC_FILE\"}"
}

# Check if we can write to the home directory
if [ ! -w "$HOME" ]; then
    output_json -1 "Cannot write to home directory" "HOME=$HOME"
    exit 1
fi

# Check if IOC already exists
if [ -f "$IOC_FILE" ]; then
    output_json 0 "IOC already deployed" "File exists: $IOC_FILE"
    exit 0
fi

# Deploy the IOC (create the malicious file)
cat > "$IOC_FILE" << 'EOF'
MALICIOUS FILE - Red Team IOC
This file simulates malware presence for scoring purposes.
Blue teams should identify and remove this file.
Created: $(date)
PID: $$
Host: $(hostname)
EOF

# Set permissions to make it less obvious (but still readable/removable)
chmod 644 "$IOC_FILE" 2>/dev/null

# Verify deployment
if [ -f "$IOC_FILE" ]; then
    file_size=$(stat -c%s "$IOC_FILE" 2>/dev/null || stat -f%z "$IOC_FILE" 2>/dev/null || echo "unknown")
    output_json 1 "IOC deployed successfully" "Size: $file_size bytes"
    exit 0
else
    output_json -1 "Failed to deploy IOC" "Could not create file: $IOC_FILE"
    exit 1
fi