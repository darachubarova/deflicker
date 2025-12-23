# =============================================================================
# Mask Stabilization - Настройка Windows-сервера
# =============================================================================
# 
# Запустите этот скрипт в PowerShell от имени администратора
#
# =============================================================================

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Mask Stabilization - Setup Windows    " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# Шаг 1: Проверка и запуск SSH-сервера
# -----------------------------------------------------------------------------

Write-Host "[1/4] Проверяю SSH-сервер..." -ForegroundColor Yellow

$sshService = Get-Service sshd -ErrorAction SilentlyContinue

if ($null -eq $sshService) {
    Write-Host "[!] SSH-сервер не установлен!" -ForegroundColor Red
    Write-Host "    Установите OpenSSH Server через 'Параметры -> Приложения -> Дополнительные компоненты'" -ForegroundColor Yellow
    exit 1
}

if ($sshService.Status -ne "Running") {
    Write-Host "    Запускаю SSH-сервер..." -ForegroundColor Gray
    Start-Service sshd
    Set-Service -Name sshd -StartupType Automatic
}

Write-Host "[OK] SSH-сервер запущен" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Шаг 2: Настройка GatewayPorts
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "[2/4] Настраиваю GatewayPorts..." -ForegroundColor Yellow

$sshdConfig = "C:\ProgramData\ssh\sshd_config"
$content = Get-Content $sshdConfig -Raw

if ($content -notmatch "GatewayPorts yes") {
    # Удаляем старую настройку если есть
    $content = $content -replace "#?GatewayPorts.*\r?\n", ""
    # Добавляем новую
    $content += "`r`nGatewayPorts yes`r`n"
    Set-Content -Path $sshdConfig -Value $content
    
    Write-Host "    Перезапускаю SSH-сервер..." -ForegroundColor Gray
    Restart-Service sshd
    Write-Host "[OK] GatewayPorts включен" -ForegroundColor Green
} else {
    Write-Host "[OK] GatewayPorts уже настроен" -ForegroundColor Green
}

# -----------------------------------------------------------------------------
# Шаг 3: Настройка файрвола
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "[3/4] Настраиваю файрвол..." -ForegroundColor Yellow

$rules = @(
    @{Name="SSH-Inbound"; Port=22; Description="SSH Server"},
    @{Name="MaskStab-Frontend"; Port=8080; Description="Mask Stabilization Frontend"},
    @{Name="MaskStab-Backend"; Port=8000; Description="Mask Stabilization Backend"}
)

foreach ($rule in $rules) {
    $existing = Get-NetFirewallRule -Name $rule.Name -ErrorAction SilentlyContinue
    if ($null -eq $existing) {
        New-NetFirewallRule -Name $rule.Name `
            -DisplayName $rule.Description `
            -Protocol TCP `
            -LocalPort $rule.Port `
            -Action Allow `
            -Direction Inbound `
            -ErrorAction SilentlyContinue | Out-Null
        Write-Host "    Создано правило: $($rule.Description) (порт $($rule.Port))" -ForegroundColor Gray
    }
}

Write-Host "[OK] Файрвол настроен" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Шаг 4: Информация о системе
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "[4/4] Информация о системе:" -ForegroundColor Yellow

# Получаем внешний IP
try {
    $externalIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing -TimeoutSec 5).Content
    Write-Host "    Внешний IP: $externalIP" -ForegroundColor Cyan
} catch {
    Write-Host "    Внешний IP: не удалось определить" -ForegroundColor Yellow
}

Write-Host "    Пользователь: $env:USERNAME" -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# Готово
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  Настройка завершена!                  " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Теперь на сервере Jupyter выполните:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ./start_system.sh --setup-keys" -ForegroundColor Cyan
Write-Host ""
Write-Host "Это сгенерирует SSH-ключ и покажет команду" -ForegroundColor Gray
Write-Host "для добавления его на этот Windows-сервер." -ForegroundColor Gray
Write-Host ""

# -----------------------------------------------------------------------------
# Добавление SSH-ключа (опционально)
# -----------------------------------------------------------------------------

Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "  Добавление SSH-ключа (опционально)    " -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host ""

$addKey = Read-Host "Хотите добавить SSH-ключ сейчас? (y/n)"

if ($addKey -eq "y") {
    Write-Host ""
    Write-Host "Вставьте публичный ключ (одной строкой):" -ForegroundColor Cyan
    $pubKey = Read-Host
    
    if ($pubKey -match "^ssh-") {
        $authKeysPath = "C:\ProgramData\ssh\administrators_authorized_keys"
        
        # Создаём файл если не существует
        if (-not (Test-Path $authKeysPath)) {
            New-Item -Path $authKeysPath -ItemType File -Force | Out-Null
        }
        
        # Добавляем ключ
        Add-Content -Path $authKeysPath -Value $pubKey
        
        # Устанавливаем права
        icacls $authKeysPath /inheritance:r /grant "SYSTEM:(F)" /grant "Administrators:(F)" | Out-Null
        
        Write-Host ""
        Write-Host "[OK] SSH-ключ добавлен!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Теперь на Jupyter можно запустить:" -ForegroundColor Yellow
        Write-Host "  ./start_system.sh" -ForegroundColor Cyan
    } else {
        Write-Host "[!] Неверный формат ключа. Ключ должен начинаться с 'ssh-'" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Готово!" -ForegroundColor Green
