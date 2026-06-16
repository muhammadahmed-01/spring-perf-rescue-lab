#!/usr/bin/env pwsh
# Run k6 load tests for buggy and fixed endpoints (~100k requests each).
param(
    [string]$BaseUrl = "http://localhost:8080",
    [int]$Vus = 100,
    [int]$Iterations = 100000,
    [string]$MaxDuration = "15m"
)

$ErrorActionPreference = "Stop"
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')

Write-Host "Waiting for $BaseUrl/actuator/health ..."
for ($i = 1; $i -le 90; $i++) {
    try {
        $h = Invoke-RestMethod -Uri "$BaseUrl/actuator/health" -TimeoutSec 3
        if ($h.status -eq 'UP') { break }
    } catch {}
    Start-Sleep -Seconds 2
}

New-Item -ItemType Directory -Force -Path load/results | Out-Null

Write-Host "Warmup (500 requests on fixed path)..."
k6 run -e BASE_URL=$BaseUrl -e ENDPOINT=/api/orders/fixed -e MODE=warmup `
  -e VUS=25 -e ITERATIONS=500 -e MAX_DURATION=2m load/k6-load.js | Out-Null

Write-Host "`n=== Buggy endpoint ($Iterations requests, $Vus VUs) ==="
k6 run -e BASE_URL=$BaseUrl -e ENDPOINT=/api/orders/buggy -e MODE=buggy `
  -e VUS=$Vus -e ITERATIONS=$Iterations -e MAX_DURATION=$MaxDuration load/k6-load.js

Write-Host "`n=== Fixed endpoint ($Iterations requests, $Vus VUs) ==="
k6 run -e BASE_URL=$BaseUrl -e ENDPOINT=/api/orders/fixed -e MODE=fixed `
  -e VUS=$Vus -e ITERATIONS=$Iterations -e MAX_DURATION=$MaxDuration load/k6-load.js

Write-Host "`nQuery counts (single request):"
(Invoke-RestMethod -Uri "$BaseUrl/api/orders/stats/buggy") | ConvertTo-Json -Compress
(Invoke-RestMethod -Uri "$BaseUrl/api/orders/stats/fixed") | ConvertTo-Json -Compress
