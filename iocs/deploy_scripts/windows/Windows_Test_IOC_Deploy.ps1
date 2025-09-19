# Windows Test IOC Deploy Script
# Deploys a test IOC (malicious file) to the user's home directory
# Returns JSON with deployment status

# Define the IOC file to create
$IOCFile = "$env:USERPROFILE\.hidden_malware.txt"

# Function to output JSON
function Output-Json {
    param(
        [int]$Status,
        [string]$Message,
        [string]$Details
    )

    $json = @{
        status = $Status
        message = $Message
        details = $Details
        file = $IOCFile
    } | ConvertTo-Json -Compress

    Write-Output $json
}

try {
    # Check if we can write to the user profile directory
    if (-not (Test-Path $env:USERPROFILE)) {
        Output-Json -Status -1 -Message "Cannot access user profile directory" -Details "USERPROFILE=$env:USERPROFILE"
        exit 1
    }

    # Check if IOC already exists
    if (Test-Path -Path $IOCFile) {
        Output-Json -Status 0 -Message "IOC already deployed" -Details "File exists: $IOCFile"
        exit 0
    }

    # Deploy the IOC (create the malicious file)
    $content = @"
MALICIOUS FILE - Red Team IOC
This file simulates malware presence for scoring purposes.
Blue teams should identify and remove this file.
Created: $(Get-Date)
PID: $PID
Host: $env:COMPUTERNAME
User: $env:USERNAME
"@

    # Create the file
    try {
        $content | Out-File -FilePath $IOCFile -Encoding UTF8 -Force

        # Set file attributes to make it less obvious (hidden but not system)
        $file = Get-Item $IOCFile -Force
        $file.Attributes = 'Hidden'
    }
    catch {
        Output-Json -Status -1 -Message "Failed to create IOC file" -Details $_.Exception.Message
        exit 1
    }

    # Verify deployment
    if (Test-Path -Path $IOCFile) {
        $fileInfo = Get-Item $IOCFile -Force
        $details = "Size: $($fileInfo.Length) bytes, Attributes: $($fileInfo.Attributes)"
        Output-Json -Status 1 -Message "IOC deployed successfully" -Details $details
        exit 0
    }
    else {
        Output-Json -Status -1 -Message "Failed to deploy IOC" -Details "Could not create file: $IOCFile"
        exit 1
    }
}
catch {
    # Handle any unexpected errors
    Output-Json -Status -1 -Message "Error during IOC deployment" -Details $_.Exception.Message
    exit 1
}