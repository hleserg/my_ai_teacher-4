# PowerShell скрипт для управления AI Learning Bot
param(
    [Parameter(Position=0)]
    [string]$Command
)

Write-Host "🤖 AI Learning Bot - Команды управления" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

switch ($Command) {
    "start" {
        Write-Host "🚀 Запуск всех сервисов..." -ForegroundColor Green
        docker-compose up -d
    }
    "stop" {
        Write-Host "⏹️ Остановка всех сервисов..." -ForegroundColor Yellow
        docker-compose down
    }
    "restart" {
        Write-Host "🔄 Перезапуск бота..." -ForegroundColor Blue
        docker-compose restart bot
    }
    "logs" {
        Write-Host "📋 Просмотр логов бота..." -ForegroundColor Magenta
        docker-compose logs -f bot
    }
    "logs-all" {
        Write-Host "📋 Просмотр всех логов..." -ForegroundColor Magenta
        docker-compose logs -f
    }
    "status" {
        Write-Host "📊 Статус сервисов..." -ForegroundColor Cyan
        docker-compose ps
    }
    "health" {
        Write-Host "🏥 Проверка работоспособности..." -ForegroundColor Green
        python health_check.py
    }
    "update" {
        Write-Host "🔄 Обновление и пересборка..." -ForegroundColor Blue
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
    }
    "clean" {
        Write-Host "🧹 Полная очистка (УДАЛЯЕТ ВСЕ ДАННЫЕ!)..." -ForegroundColor Red
        $confirmation = Read-Host "Вы уверены? (y/N)"
        if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
            docker-compose down -v
            docker system prune -f
        } else {
            Write-Host "Операция отменена" -ForegroundColor Yellow
        }
    }
    "setup" {
        Write-Host "⚙️ Первоначальная настройка..." -ForegroundColor Green
        if (-not (Test-Path ".env")) {
            Copy-Item ".env.example" -Destination ".env"
            Write-Host "✅ Создан .env файл" -ForegroundColor Green
            Write-Host "⚠️  ОБЯЗАТЕЛЬНО укажите TELEGRAM_BOT_TOKEN в .env файле!" -ForegroundColor Red
        } else {
            Write-Host "⚠️  .env файл уже существует" -ForegroundColor Yellow
        }
    }
    default {
        Write-Host "Доступные команды:" -ForegroundColor White
        Write-Host ""
        Write-Host "🚀 Основные команды:" -ForegroundColor Green
        Write-Host "  manage.ps1 setup    - Первоначальная настройка"
        Write-Host "  manage.ps1 start    - Запуск всех сервисов"
        Write-Host "  manage.ps1 stop     - Остановка всех сервисов"
        Write-Host "  manage.ps1 restart  - Перезапуск бота"
        Write-Host ""
        Write-Host "📊 Мониторинг:" -ForegroundColor Cyan
        Write-Host "  manage.ps1 status   - Статус сервисов"
        Write-Host "  manage.ps1 logs     - Логи бота"
        Write-Host "  manage.ps1 logs-all - Все логи"
        Write-Host "  manage.ps1 health   - Проверка здоровья"
        Write-Host ""
        Write-Host "🔧 Обслуживание:" -ForegroundColor Magenta
        Write-Host "  manage.ps1 update   - Обновление и пересборка"
        Write-Host "  manage.ps1 clean    - Полная очистка"
        Write-Host ""
        Write-Host "📚 Быстрый старт:" -ForegroundColor Yellow
        Write-Host "  1. manage.ps1 setup"
        Write-Host "  2. Отредактируйте .env файл"
        Write-Host "  3. manage.ps1 start"
        Write-Host "  4. manage.ps1 logs"
    }
}
