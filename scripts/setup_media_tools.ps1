$ErrorActionPreference = "Continue"

Write-Host "Verificando dependências de mídia..." -ForegroundColor Cyan

# Função auxiliar
function Check-Command($cmd) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        Write-Host "[OK] $cmd detectado." -ForegroundColor Green
        return $true
    }
    Write-Host "[X] $cmd NÃO encontrado." -ForegroundColor Red
    return $false
}

$needsFfmpeg = !(Check-Command "ffmpeg") -or !(Check-Command "ffprobe")
$needsMagick = !(Check-Command "magick")

if ($needsFfmpeg) {
    Write-Host "Instalando FFmpeg via choco..." -ForegroundColor Yellow
    choco install ffmpeg -y
}

if ($needsMagick) {
    Write-Host "Instalando ImageMagick via choco..." -ForegroundColor Yellow
    choco install imagemagick -y
}

if (-not $needsFfmpeg -and -not $needsMagick) {
    Write-Host "Todas as dependências estão prontas! ✅" -ForegroundColor Green
} else {
    Write-Host "Instalações concluídas. Por favor, feche e abra o terminal novamente (ou use refreshenv) para atualizar o PATH. ✅" -ForegroundColor Green
}
