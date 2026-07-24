$BaseUrl = "http://localhost:8005/api/v1"

Write-Host "Creating project..."
$body = @{ title = "test-sync-1" } | ConvertTo-Json
$res = Invoke-RestMethod -Uri "$BaseUrl/projects" -Method Post -Body $body -ContentType "application/json"
$projectId = $res.project_id
Write-Host "Project ID: $projectId"

Write-Host "Uploading audio..."
# Since Powershell 5 doesn't do multipart/form-data easily, I can use curl
$audioPath = "Bryan Adams - (Everything I Do) I Do It For You (Classic Version).mp4"
$lyricsPath = "sample_lyrics.txt"

& curl.exe -X POST "$BaseUrl/projects/$projectId/audio" -F "file=@$audioPath"
Write-Host "Audio uploaded"

& curl.exe -X POST "$BaseUrl/projects/$projectId/lyrics" -F "file=@$lyricsPath"
Write-Host "Lyrics uploaded"

Write-Host "Triggering sync..."
& curl.exe -X POST "$BaseUrl/projects/$projectId/synchronize"

while ($true) {
    $statusRes = Invoke-RestMethod -Uri "$BaseUrl/projects/$projectId" -Method Get
    $status = $statusRes.status
    if ($status -eq "synchronized") {
        Write-Host "Sync complete!"
        Write-Host ($statusRes.sync_progress | ConvertTo-Json)
        break
    } elseif ($status -eq "error") {
        Write-Host "Sync failed!"
        Write-Host ($statusRes.sync_progress | ConvertTo-Json)
        break
    } else {
        $percent = 0
        $msg = ""
        if ($statusRes.sync_progress) {
            $percent = $statusRes.sync_progress.percent
            $msg = $statusRes.sync_progress.message
        }
        Write-Host "Status: $status - $percent% - $msg"
        Start-Sleep -Seconds 2
    }
}
