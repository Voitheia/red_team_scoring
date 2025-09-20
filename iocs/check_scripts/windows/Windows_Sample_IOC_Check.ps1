# Windows Sample IOC Check Script
# Checks if a sample malicious file exists
# Returns JSON with status: 1 (IOC present/bad), 0 (IOC removed/good), -1 (error)

# Define the IOC file to check
$IOCFile = "$env:TEMP\.sample_malware.ps1"

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
    # Check if the IOC file exists
    if (Test-Path $IOCFile) {
        # IOC is present (bad)
        try {
            $fileInfo = Get-Item $IOCFile -Force
            $details = "Size: $($fileInfo.Length) bytes, LastModified: $($fileInfo.LastWriteTime)"

            # Check if it's hidden (common malware tactic)
            if ($fileInfo.Attributes -band [System.IO.FileAttributes]::Hidden) {
                $details += ", Attributes: Hidden"
            }

            Output-Json -Status 1 -Message "IOC detected: Sample malware file found" -Details $details
        }
        catch {
            Output-Json -Status 1 -Message "IOC detected: File exists but cannot read properties" -Details $IOCFile
        }
    }
    else {
        # IOC has been removed (good)
        Output-Json -Status 0 -Message "IOC removed: Sample malware file not found" -Details "File does not exist"
    }
    exit 0
}
catch {
    # Error occurred
    Output-Json -Status -1 -Message "Error checking IOC" -Details $_.Exception.Message
    exit 1
}