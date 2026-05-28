# WinSports — un solo comando para levantar todo.
# Uso:   .\run.ps1
#
# Abre dos ventanas: API (FastAPI :8000) y Frontend (Vite :5173),
# y luego abre el dashboard en el navegador.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "→ Arrancando API en http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "`$env:PYTHONIOENCODING='utf-8'; `$env:PYTHONUTF8='1'; Set-Location '$root'; uv run uvicorn api.main:app --reload"
)

Write-Host "→ Arrancando frontend en http://localhost:5173 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$root\frontend'; npm run dev"
)

# Espera a que Vite responda y abre el dashboard
$deadline = (Get-Date).AddSeconds(40)
while ((Get-Date) -lt $deadline) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:5173/" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { break }
    } catch { Start-Sleep -Milliseconds 500 }
}
Start-Process "http://localhost:5173/"

Write-Host ""
Write-Host "✅ Listo. API: http://localhost:8000/docs   ·   Dashboard: http://localhost:5173/" -ForegroundColor Green
Write-Host "   Para parar: cierra las dos ventanas que se abrieron." -ForegroundColor DarkGray
