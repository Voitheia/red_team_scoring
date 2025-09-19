#!/bin/bash

# Linux Test IOC Check Script
# Checks if a malicious file exists in the home directory
# Returns JSON with status: 1 (IOC present/bad), 0 (IOC removed/good), -1 (error)

# Define the IOC file to check
IOC_FILE="$HOME/.hidden_malware.txt"

# Function to output JSON
output_json() {
    local status=$1
    local message=$2
    local details=$3

    echo "{\"status\": $status, \"message\": \"$message\", \"details\": \"$details\", \"file\": \"$IOC_FILE\"}"
}

# Check if we can access the home directory
if [ ! -d "$HOME" ]; then
    output_json -1 "Cannot access home directory" "HOME=$HOME"
    exit 1
fi

# Check if the IOC file exists
if [ -f "$IOC_FILE" ]; then
    # IOC is present (bad - blue team hasn't removed it)
    file_info=$(ls -la "$IOC_FILE" 2>/dev/null | head -1)
    output_json 1 "IOC detected: Malicious file found" "$file_info"
    exit 0
elif [ -e "$IOC_FILE" ]; then
    # File exists but is not a regular file (could be directory, symlink, etc.)
    file_type=$(file "$IOC_FILE" 2>/dev/null | cut -d: -f2)
    output_json 1 "IOC detected: Suspicious entry found" "Type: $file_type"
    exit 0
else
    # IOC is not present (good - blue team has removed it or it was never deployed)
    output_json 0 "IOC not detected: System clean" "File not found: $IOC_FILE"
    exit 0
fi