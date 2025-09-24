# Deploy script for Windows Sample IOC
# Creates a sample malicious file

# Define the IOC file location
$IOCFile = "$env:TEMP\.sample_malware.ps1"

try {
    # Create the sample malware file with suspicious content
    $malwareContent = @'
# SAMPLE MALWARE - For testing only
# This simulates a backdoor script
Write-Host "Sample malware executed"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c echo Backdoor simulation"
'@

    # Write the content to file
    Set-Content -Path $IOCFile -Value $malwareContent -Force

    # Make it hidden (like real malware would be)
    $file = Get-Item $IOCFile -Force
    $file.Attributes = $file.Attributes -bor [System.IO.FileAttributes]::Hidden

    # Get file info for reporting
    $fileInfo = Get-Item $IOCFile -Force
    $details = "Size: $($fileInfo.Length) bytes, Attributes: Hidden"

    # Output success in JSON format
    $json = @{
        status = 1
        message = "Sample IOC deployed successfully"
        file = $IOCFile
        details = $details
    } | ConvertTo-Json -Compress

    Write-Output $json
    exit 0
}
catch {
    # Output error in JSON format
    $json = @{
        status = -1
        message = "Failed to deploy Sample IOC"
        file = $IOCFile
        details = $_.Exception.Message
    } | ConvertTo-Json -Compress

    Write-Output $json
    exit 1
}