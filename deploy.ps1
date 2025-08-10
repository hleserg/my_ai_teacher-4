# Скрипт развертывания AI Learning Bot для Windows PowerShell
# 
# Использование:
# .\deploy.ps1 [development|production|monitoring]

param(
    [string]$Mode = "production"
)

# Цвета для вывода
function Write-Info($message) {
    Write-Host "[INFO] $message" -ForegroundColor Blue
}

function Write-Success($message) {
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

Write-Info "🚀 Развертывание AI Learning Bot в режиме: $Mode"

# Проверка Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker не установлен. Установите Docker Desktop"
    exit 1
}

if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Error "Docker Compose не установлен"
    exit 1
}

# Определение файлов конфигурации
switch ($Mode) {
    "development" {
        $ComposeFile = "docker-compose.yml"
        $EnvFile = ".env.local"
    }
    "production" {
        $ComposeFile = "docker-compose.prod.yml" 
        $EnvFile = ".env.prod"
    }
    "monitoring" {
        $ComposeFile = "docker-compose.prod.yml"
        $EnvFile = ".env.prod"
        $Profiles = "--profile monitoring"
    }
    default {
        Write-Error "Неизвестный режим: $Mode. Используйте: development, production, monitoring"
        exit 1
    }
}

# Проверка файлов
if (!(Test-Path $ComposeFile)) {
    Write-Error "Файл $ComposeFile не найден!"
    exit 1
}

if (!(Test-Path $EnvFile)) {
    Write-Warning "Файл $EnvFile не найден. Создаем из примера..."
    
    if (($Mode -eq "production") -or ($Mode -eq "monitoring")) {
        if (Test-Path ".env.prod.example") {
            Copy-Item ".env.prod.example" $EnvFile
            Write-Info "Файл $EnvFile создан из .env.prod.example"
            Write-Warning "⚠️  ВАЖНО: Отредактируйте $EnvFile и заполните все переменные!"
            Read-Host "Нажмите Enter после редактирования файла"
        } else {
            Write-Error "Файл .env.prod.example не найден!"
            exit 1
        }
    }
}

# Проверка переменных
Write-Info "🔍 Проверка конфигурации..."

if ((Get-Content $EnvFile -Raw) -match "your_telegram_bot_token_here|your_grok_api_key_here") {
    Write-Error "В файле $EnvFile есть незаполненные переменные!"
    exit 1
}

# Создание директорий
Write-Info "📁 Создание директорий..."
$dirs = @("logs", "config", "ssl", "nginx/logs", "monitoring/grafana/provisioning")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
    }
}

# Остановка контейнеров
Write-Info "🛑 Остановка существующих контейнеров..."
& docker-compose -f $ComposeFile down --remove-orphans 2>$null

# Сборка образов
Write-Info "🔨 Сборка Docker образов..."
& docker-compose -f $ComposeFile build --no-cache

# Запуск сервисов
Write-Info "🚀 Запуск сервисов..."

if ($Mode -eq "monitoring") {
    Write-Info "Запуск с профилем мониторинга..."
    & docker-compose -f $ComposeFile --env-file $EnvFile --profile monitoring up -d
} else {
    & docker-compose -f $ComposeFile --env-file $EnvFile up -d
}

# Ожидание запуска
Write-Info "⏳ Ожидание запуска сервисов..."
Start-Sleep -Seconds 10

# Проверка статуса
Write-Info "📊 Статус сервисов:"
& docker-compose -f $ComposeFile ps

# Проверка здоровья
Write-Info "🔍 Проверка работоспособности..."
Start-Sleep -Seconds 15

try {
    & docker-compose -f $ComposeFile exec -T bot python health_check.py
    Write-Success "✅ Система работает корректно!"
} catch {
    Write-Warning "⚠️  Проблемы с работоспособностью системы"
}

# Информация
Write-Success "🎉 Развертывание завершено!"
Write-Host ""
Write-Info "📋 Полезные команды:"
Write-Host "  Логи бота:           docker-compose -f $ComposeFile logs -f bot"
Write-Host "  Логи планировщика:   docker-compose -f $ComposeFile logs -f scheduler"  
Write-Host "  Статус сервисов:     docker-compose -f $ComposeFile ps"
Write-Host "  Остановка:           docker-compose -f $ComposeFile down"
Write-Host "  Перезапуск:          docker-compose -f $ComposeFile restart"

if ($Mode -eq "monitoring") {
    Write-Host ""
    Write-Info "🔗 Ссылки для мониторинга:"
    Write-Host "  Grafana:    http://localhost:3000 (admin/admin123)"
    Write-Host "  Prometheus: http://localhost:9090"
}

Write-Host ""
Write-Info "📝 Логи находятся в директории: .\logs\"
Write-Info "⚙️  Конфигурация: $EnvFile"

# Финальная проверка
$status = & docker-compose -f $ComposeFile ps
if ($status -match "Up") {
    Write-Success "🚀 AI Learning Bot успешно развернут и работает!"
} else {
    Write-Error "❌ Проблемы с запуском. Проверьте логи: docker-compose -f $ComposeFile logs"
    exit 1
}
