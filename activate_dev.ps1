# Скрипт активации виртуальной среды для AI Learning Bot
Write-Host "🔧 Активация виртуальной среды для AI Learning Bot..." -ForegroundColor Cyan

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Виртуальная среда не найдена!" -ForegroundColor Red
    Write-Host "Создайте виртуальную среду командой: python -m venv venv" -ForegroundColor Yellow
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

& ".\venv\Scripts\Activate.ps1"

Write-Host "✅ Виртуальная среда активирована!" -ForegroundColor Green
Write-Host "Python путь: $env:VIRTUAL_ENV\Scripts\python.exe" -ForegroundColor Gray

Write-Host ""
Write-Host "📋 Доступные команды:" -ForegroundColor Yellow
Write-Host "  python main.py           - Запуск бота" -ForegroundColor White
Write-Host "  python scheduler.py      - Запуск планировщика" -ForegroundColor White  
Write-Host "  python health_check.py   - Проверка системы" -ForegroundColor White
Write-Host "  python test_simple.py    - Быстрые тесты" -ForegroundColor White
Write-Host "  pip list                 - Список пакетов" -ForegroundColor White
Write-Host ""
