#!/bin/bash
# Deploy script for Linux Sample IOC
# Creates a sample malicious file

IOC_FILE="/tmp/.sample_malware"

# Create the sample malware file with suspicious content
cat > "$IOC_FILE" << 'EOF'
#!/bin/bash
# SAMPLE MALWARE - For testing only
# This simulates a backdoor script
echo "Sample malware executed"
EOF

# Make it executable (like real malware would be)
chmod 755 "$IOC_FILE"

# Get file info for reporting
file_info=$(ls -la "$IOC_FILE" 2>/dev/null)

# Output success in JSON format
echo "{\"status\": 1, \"message\": \"Sample IOC deployed successfully\", \"details\": \"$file_info\", \"file\": \"$IOC_FILE\"}"