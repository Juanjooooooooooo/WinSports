# WinSports — un solo comando para levantar todo.
# Uso:   .\run.ps1
#
# Abre dos ventanas: API (FastAPI :8000) y Frontend (Vite :5173).
# Espera a que la API responda CON DATOS (conexión a Atlas incluida) antes de
# abrir el navegador — así el dashboard nunca carga en blanco.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

# ── 0. Liberar puertos si quedaron procesos viejos ───────────
function Liberar-Puerto($puerto) {
    $conns = Get-NetTCPConnection -LocalPort $puerto -State Listen -ErrorAction SilentlyContinue
    foreach ($c in ($conns | Select-Object -Unique OwningProcess)) {
        Write-Host "  · Puerto $puerto ocupado — cerrando proceso viejo (PID $($c.OwningProcess))" -ForegroundColor DarkYellow
        taskkill /T /F /PID $c.OwningProcess 2>$null | Out-Null
    }
}
Liberar-Puerto 8000
Liberar-Puerto 5173

# ── 1. Arrancar API y frontend en sus ventanas ───────────────
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

# ── 2. Esperar a que la API devuelva DATOS (no solo el health) ─
# /api/overview/top-content consulta Atlas de verdad: si responde 200,
# el dashboard va a cargar con todo.
Write-Host "→ Esperando a que la API conecte con Atlas (hasta 90s) ..." -ForegroundColor Cyan
$apiLista = $false
$deadline = (Get-Date).AddSeconds(90)
while ((Get-Date) -lt $deadline) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/api/overview/top-content" -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200 -and $r.Content.Length -gt 10) { $apiLista = $true; break }
    } catch { Start-Sleep -Milliseconds 800 }
}
if (-not $apiLista) {
    Write-Host ""
    Write-Host "❌ La API no respondió con datos en 90s." -ForegroundColor Red
    Write-Host "   Revisa la ventana de la API: suele ser internet caído, el .env sin" -ForegroundColor Red
    Write-Host "   MONGO_URI, o la IP no autorizada en Atlas (Network Access)." -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ API con datos de Atlas" -ForegroundColor Green

# ── 3. Esperar al frontend y abrir el navegador ──────────────
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
