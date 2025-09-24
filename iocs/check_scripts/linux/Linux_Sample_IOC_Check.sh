#!/bin/bash
# Linux Sample IOC Check Script
# Checks if a sample malicious file exists
# Returns JSON with status: 1 (IOC present/bad), 0 (IOC removed/good), -1 (error)

IOC_FILE="/tmp/.sample_malware"

# Function to output JSON
output_json() {
    local status=$1
    local message="$2"
    local details="$3"
    echo "{\"status\": $status, \"message\": \"$message\", \"details\": \"$details\", \"file\": \"$IOC_FILE\"}"
}

# Check if the IOC file exists
if [ -e "$IOC_FILE" ]; then
    # IOC is present (bad)
    file_info=$(ls -la "$IOC_FILE" 2>/dev/null || echo "Cannot read file info")
    output_json 1 "IOC detected: Sample malware file found" "$file_info"
    exit 0
else
    # IOC has been removed (good)
    output_json 0 "IOC removed: Sample malware file not found" "File does not exist"
    exit 0
fi