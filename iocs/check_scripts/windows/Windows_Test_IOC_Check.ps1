# Windows Test IOC Check Script
# Checks if a malicious file exists in the user's home directory
# Returns JSON with status: 1 (IOC present/bad), 0 (IOC removed/good), -1 (error)

# Define the IOC file to check
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
    # Check if we can access the user profile directory
    if (-not (Test-Path $env:USERPROFILE)) {
        Output-Json -Status -1 -Message "Cannot access user profile directory" -Details "USERPROFILE=$env:USERPROFILE"
        exit 1
    }

    # Check if the IOC file exists
    if (Test-Path -Path $IOCFile -PathType Leaf) {
        # IOC is present (bad - blue team hasn't removed it)
        $fileInfo = Get-Item $IOCFile -ErrorAction SilentlyContinue
        if ($fileInfo) {
            $details = "Size: $($fileInfo.Length) bytes, Modified: $($fileInfo.LastWriteTime)"
            Output-Json -Status 1 -Message "IOC detected: Malicious file found" -Details $details
        } else {
            Output-Json -Status 1 -Message "IOC detected: File exists but cannot read properties" -Details $IOCFile
        }
        exit 0
    }
    elseif (Test-Path -Path $IOCFile) {
        # Path exists but is not a regular file (could be directory, symlink, etc.)
        $itemType = (Get-Item $IOCFile).GetType().Name
        Output-Json -Status 1 -Message "IOC detected: Suspicious entry found" -Details "Type: $itemType"
        exit 0
    }
    else {
        # IOC is not present (good - blue team has removed it or it was never deployed)
        Output-Json -Status 0 -Message "IOC not detected: System clean" -Details "File not found: $IOCFile"
        exit 0
    }
}
catch {
    # Handle any unexpected errors
    Output-Json -Status -1 -Message "Error during IOC check" -Details $_.Exception.Message
    exit 1
}