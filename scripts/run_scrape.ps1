Param(
    [string]$url = ''
)

# Usage:
# .\run_scrape.ps1 -url 'https://www.justdial.com/Mumbai/Dentists/nct-10156331?trkid=28470-mumbai&term=&cbflg=1'

if (-not $url -or $url -eq '') {
    Write-Host "No URL provided, using example file backend/tmp/temp_url_example.txt"
    $example = Join-Path -Path (Split-Path -Parent $PSScriptRoot) -ChildPath 'backend\tmp\temp_url_example.txt'
    if (Test-Path $example) {
        $url = Get-Content $example -Raw
        $url = $url.Trim()
    } else {
        Write-Error "No URL provided and example file not found."
        exit 1
    }
}

Write-Host "Triggering scraper for URL: $url"

$payload = @{ url = $url } | ConvertTo-Json

try {
    $resp = Invoke-RestMethod -Uri 'http://localhost:5000/api/scrape' -Method Post -Body $payload -ContentType 'application/json' -TimeoutSec 600
    if ($resp.success) {
        Write-Host "Scrape succeeded. File:" $resp.filename
        $out = $resp.data | ConvertTo-Csv -NoTypeInformation
        $out | Select-Object -First 30 | ForEach-Object { Write-Host $_ }
    } else {
        Write-Error "Scrape failed: $($resp.error)"
    }
} catch {
    Write-Error "Request failed: $($_.Exception.Message)"
}
