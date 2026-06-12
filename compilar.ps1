# WinSports — un solo comando: verifica front y back, y los deja funcionando.
# Uso:   .\compilar.ps1
#
# Corre en orden: tests del backend, build del frontend y tests del frontend.
# Si todo pasa, levanta la API (:8000) y el dashboard (:5173) con run.ps1 y
# abre el navegador. Si algo falla, NO levanta nada y muestra qué falló.
#
# El informe LaTeX va aparte:
#   pdflatex --enable-installer -interaction=nonstopmode InformeFinal.tex  (x2)

$ErrorActionPreference = "Continue"
$root = $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$resultados = @()

function Paso($nombre, $directorio, $accion) {
    Write-Host ""
    Write-Host "→ $nombre ..." -ForegroundColor Cyan
    Push-Location $directorio
    $inicio = Get-Date
    & $accion
    $ok = ($LASTEXITCODE -eq 0)
    $duracion = "{0:n0}s" -f ((Get-Date) - $inicio).TotalSeconds
    Pop-Location
    $script:resultados += [pscustomobject]@{ Paso = $nombre; OK = $ok; Tiempo = $duracion }
    if ($ok) { Write-Host "  ✅ $nombre ($duracion)" -ForegroundColor Green }
    else     { Write-Host "  ❌ $nombre FALLÓ — revisa la salida de arriba" -ForegroundColor Red }
}

Paso "Tests del backend (pytest)" $root {
    uv run pytest -q
}

Paso "Build del frontend (vite)" "$root\frontend" {
    npm run build
}

Paso "Tests del frontend (vitest)" "$root\frontend" {
    npm run test
}

# ── Resumen ──────────────────────────────────────────────────
Write-Host ""
Write-Host "════════════ RESUMEN ════════════" -ForegroundColor Yellow
foreach ($r in $resultados) {
    $icono = if ($r.OK) { "✅" } else { "❌" }
    $color = if ($r.OK) { "Green" } else { "Red" }
    Write-Host ("  {0} {1}  ({2})" -f $icono, $r.Paso, $r.Tiempo) -ForegroundColor $color
}
Write-Host ""

$fallos = @($resultados | Where-Object { -not $_.OK })
if ($fallos.Count -gt 0) {
    Write-Host "❌ Falló: $($fallos.Paso -join ', ') — no se levanta nada hasta arreglarlo." -ForegroundColor Red
    exit 1
}

# ── Todo verde: dejar front y back funcionando ───────────────
Write-Host "✅ Todo en orden. Levantando API y dashboard..." -ForegroundColor Green
& "$root\run.ps1"
