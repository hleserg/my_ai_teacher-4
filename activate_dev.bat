@echo off
echo 🔧 Активация виртуальной среды для AI Learning Bot...

if not exist "venv\Scripts\activate.bat" (
    echo ❌ Виртуальная среда не найдена!
    echo Создайте виртуальную среду командой: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo ✅ Виртуальная среда активирована!
echo Python путь: %VIRTUAL_ENV%\Scripts\python.exe

echo.
echo 📋 Доступные команды:
echo   python main.py           - Запуск бота
echo   python scheduler.py      - Запуск планировщика  
echo   python health_check.py   - Проверка системы
echo   python test_simple.py    - Быстрые тесты
echo   pip list                 - Список пакетов
echo.

cmd /k
