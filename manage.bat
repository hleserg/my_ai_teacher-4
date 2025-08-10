@echo off
REM Batch файл для управления AI Learning Bot

echo 🤖 AI Learning Bot - Команды управления
echo ==========================================

if "%1"=="start" (
    echo 🚀 Запуск всех сервисов...
    docker-compose up -d
    goto :eof
)

if "%1"=="stop" (
    echo ⏹️ Остановка всех сервисов...
    docker-compose down
    goto :eof
)

if "%1"=="restart" (
    echo 🔄 Перезапуск бота...
    docker-compose restart bot
    goto :eof
)

if "%1"=="logs" (
    echo 📋 Просмотр логов бота...
    docker-compose logs -f bot
    goto :eof
)

if "%1"=="status" (
    echo 📊 Статус сервисов...
    docker-compose ps
    goto :eof
)

if "%1"=="health" (
    echo 🏥 Проверка работоспособности...
    python health_check.py
    goto :eof
)

if "%1"=="setup" (
    echo ⚙️ Первоначальная настройка...
    if not exist .env (
        copy .env.example .env
        echo ✅ Создан .env файл
        echo ⚠️  ОБЯЗАТЕЛЬНО укажите TELEGRAM_BOT_TOKEN в .env файле!
    ) else (
        echo ⚠️  .env файл уже существует
    )
    goto :eof
)

echo Доступные команды:
echo.
echo 🚀 Основные команды:
echo   manage.bat setup    - Первоначальная настройка
echo   manage.bat start    - Запуск всех сервисов
echo   manage.bat stop     - Остановка всех сервисов
echo   manage.bat restart  - Перезапуск бота
echo.
echo 📊 Мониторинг:
echo   manage.bat status   - Статус сервисов
echo   manage.bat logs     - Логи бота
echo   manage.bat health   - Проверка здоровья
echo.
echo 📚 Быстрый старт:
echo   1. manage.bat setup
echo   2. Отредактируйте .env файл
echo   3. manage.bat start
echo   4. manage.bat logs
