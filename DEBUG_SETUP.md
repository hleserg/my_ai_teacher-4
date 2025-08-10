# 🐍 Настройка виртуальной среды для отладки VS Code

## ✅ Что настроено:

### 1. 📁 Файл `.vscode/settings.json`
```json
{
    "python.pythonPath": "./venv/Scripts/python.exe",
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe", 
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true
}
```

### 2. 🚀 Файл `.vscode/launch.json` 
Все конфигурации отладки теперь используют:
```json
"python": "${workspaceFolder}/venv/Scripts/python.exe"
```

### 3. 🔧 Скрипты активации
- `activate_dev.bat` - для Command Prompt
- `activate_dev.ps1` - для PowerShell

## 🎯 Как использовать отладку:

### Способ 1: VS Code Debug Panel
1. **Откройте панель отладки**: `Ctrl+Shift+D`
2. **Выберите конфигурацию**:
   - 🤖 Запуск AI Learning Bot
   - ⏰ Запуск планировщика задач  
   - 🏥 Проверка состояния системы
   - 🧪 Запуск тестов
   - 🔧 Локальная разработка
3. **Нажмите F5** или зеленую кнопку

### Способ 2: Командная строка (с активированной средой)
```bash
# Активация виртуальной среды
.\activate_dev.ps1

# Запуск с отладкой
python main.py
python scheduler.py  
python health_check.py
```

## 🔍 Проверка правильной работы:

### Проверить интерпретатор VS Code:
1. **Откройте Command Palette**: `Ctrl+Shift+P`
2. **Введите**: "Python: Select Interpreter"
3. **Выберите**: `./venv/Scripts/python.exe`

### Проверить в терминале:
```powershell
python -c "import sys; print('Executable:', sys.executable)"
# Должен показать: C:\...\my_ai_teacher 3\venv\Scripts\python.exe
```

### Проверить пакеты:
```powershell
pip list | Select-String "sqlalchemy|telegram"
# Должны быть видны установленные пакеты
```

## 🚨 Если отладка не работает:

### 1. Перезапустите VS Code
После изменения настроек рекомендуется перезапустить VS Code.

### 2. Принудительно выберите интерпретатор
- `Ctrl+Shift+P` → "Python: Select Interpreter" 
- Выберите `./venv/Scripts/python.exe`

### 3. Проверьте активацию среды
```powershell
# В терминале VS Code должен быть префикс (venv)
(venv) PS C:\...\my_ai_teacher 3>
```

### 4. Переустановите зависимости
```powershell
pip install -r requirements.txt
```

## 💡 Полезные команды:

### Быстрая активация и тест:
```powershell
.\activate_dev.ps1
python test_simple.py
```

### Проверка всех компонентов:
```powershell
python health_check.py
```

### Запуск отладки бота:
```powershell
python main.py
```

## 🎉 Готово к использованию!

Теперь вся отладка будет использовать виртуальную среду `venv` с установленными зависимостями, включая SQLAlchemy, python-telegram-bot и другие пакеты!
