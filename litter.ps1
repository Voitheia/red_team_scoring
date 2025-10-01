# Set your destination path
$destPath = "C:\Nostromo_Files"
New-Item -ItemType Directory -Force -Path $destPath | Out-Null

# Crew manifest CSV
$crewData = @"
Crew_ID,Name,Rank,Department,Assignment,Status
N001,Dallas,Captain,Command,Nostromo,Active
N002,Kane,Executive Officer,Command,Nostromo,Deceased
N003,Ripley,Warrant Officer,Command,Nostromo,Active
N004,Ash,Science Officer,Science,Nostromo,Terminated
N005,Lambert,Navigator,Navigation,Nostromo,Deceased
N006,Parker,Chief Engineer,Engineering,Nostromo,Deceased
N007,Brett,Engineering Technician,Engineering,Nostromo,Deceased
"@
$crewData | Out-File "$destPath\Crew_Manifest_180642.csv"

# Cargo manifests
1..15 | ForEach-Object {
    $cargoData = @"
Container_ID,Contents,Weight_Tons,Origin,Destination,Seal_Status
$(1..20 | ForEach-Object {
    "ORE-$("{0:D5}" -f $_),Mineral Ore Batch $(Get-Random -Min 100 -Max 999),$(Get-Random -Min 500 -Max 2000),Thedus,Earth,Sealed"
} | Out-String)
"@
    $cargoData | Out-File "$destPath\Cargo_Manifest_Sector_$_.csv"
}

# Ship logs (text files)
$logEntries = @(
    "Systems nominal. All crew accounted for. Hypersleep chambers functioning within normal parameters.",
    "Course correction completed. ETA to Earth: 10 months.",
    "Routine maintenance on primary life support systems completed.",
    "MOTHER reports minor fluctuation in coolant system. Parker investigating.",
    "Distress signal detected. Company directive 937 invoked. Investigating source.",
    "Emergency landing protocol initiated. Surface conditions: hostile.",
    "WARNING: Quarantine procedures violated. Unknown organism aboard.",
    "Life support failure in Section B. Rerouting power from auxiliary.",
    "CRITICAL: Multiple system failures. Crew casualties reported.",
    "Self-destruct sequence initiated. Authorization: Ripley, W.O."
)

1..25 | ForEach-Object {
    $date = (Get-Date).AddDays(-$(Get-Random -Max 365))
    $filename = "Ships_Log_$($date.ToString('yyyyMMdd'))_Entry$_.txt"
    $entry = $logEntries | Get-Random
    $content = @"
USCSS NOSTROMO - SHIP'S LOG
Date: $($date.ToString('yyyy-MM-dd'))
Time: $(Get-Random -Min 0 -Max 23):$(Get-Random -Min 0 -Max 59) Hours
Officer: $(('Dallas','Ripley','Kane','Ash') | Get-Random)

$entry

End Log Entry.
"@
    $content | Out-File "$destPath\$filename"
}

# System diagnostics
1..10 | ForEach-Object {
    $diagData = @"
System,Status,Last_Check,Efficiency,Notes
Life Support,$(('Operational','Degraded','Critical') | Get-Random),$(Get-Date).AddHours(-$(Get-Random -Max 48)).ToString('yyyy-MM-dd HH:mm'),$(Get-Random -Min 75 -Max 100)%,Nominal
Hyperdrive,Operational,$(Get-Date).AddDays(-$(Get-Random -Max 30)).ToString('yyyy-MM-dd HH:mm'),$(Get-Random -Min 85 -Max 100)%,Coolant levels acceptable
Navigation,Operational,$(Get-Date).AddHours(-$(Get-Random -Max 12)).ToString('yyyy-MM-dd HH:mm'),$(Get-Random -Min 90 -Max 100)%,Course locked
MOTHER Interface,Operational,$(Get-Date).AddDays(-1).ToString('yyyy-MM-dd HH:mm'),100%,All systems green
Cargo Bay,Pressurized,$(Get-Date).AddHours(-$(Get-Random -Max 72)).ToString('yyyy-MM-dd HH:mm'),N/A,Seals intact
"@
    $diagData | Out-File "$destPath\System_Diagnostic_Report_$_.csv"
}

# Special Order 937 (the infamous one)
$specialOrder = @"
PRIORITY ONE

ENSURE RETURN OF ORGANISM FOR ANALYSIS.
ALL OTHER CONSIDERATIONS SECONDARY.
CREW EXPENDABLE.

- The Company
"@
$specialOrder | Out-File "$destPath\Special_Order_937_CLASSIFIED.txt"

# Weyland-Yutani memos
$memos = @(
    "Ref: Payload bonus structure. All crew members entitled to full shares upon successful delivery.",
    "Maintenance reminder: Hypersleep chamber inspection due before next voyage.",
    "Company policy update: All distress signals must be investigated per Colonial statute.",
    "Refinery systems operating at 98% efficiency. Minor adjustments recommended.",
    "Insurance documentation requires update. See administration upon return to Gateway Station."
)

1..8 | ForEach-Object {
    $memo = $memos | Get-Random
    $content = @"
WEYLAND-YUTANI CORPORATION
Internal Memorandum

To: USCSS Nostromo Crew
From: Home Office
Date: $(Get-Date).AddDays(-$(Get-Random -Max 180)).ToString('yyyy-MM-dd')

$memo

Regards,
Corporate Administration
"@
    $content | Out-File "$destPath\WY_Memo_$_.txt"
}

Write-Host "Nostromo files created in $destPath" -ForegroundColor Green
Write-Host "In space, no one can hear you scream..." -ForegroundColor Cyan
