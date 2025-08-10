# 🛠️ Локальная разработка AI Teacher Bot

## 📋 Статус установки

✅ **Виртуальная среда Python 3.13** - настроена и активирована  
✅ **Основные зависимости** - установлены (Telegram Bot, SQLAlchemy, aiohttp)  
✅ **Импорты модулей** - все 6 модулей импортируются успешно  
✅ **GrokService** - работает корректно  
⚠️ **База данных PostgreSQL** - недоступна локально (требует C++ компилятор)  

## 🚀 Быстрый старт

### 1. Активация окружения
```bash
# В PowerShell
.\venv\Scripts\Activate.ps1

# Проверка активации (должен отображаться префикс (venv))
python --version
```

### 2. Тестирование компонентов
```bash
# Быстрый тест всех модулей
python test_simple.py

# Полная диагностика системы
python health_check.py
```

### 3. Настройка конфигурации
Отредактируйте файл `.env.local`:
```env
# Обязательные параметры для работы бота
TELEGRAM_BOT_TOKEN=ваш_токен_бота
GROK_API_KEY=ваш_ключ_grok_api

# Опциональные параметры
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### 4. Запуск для разработки
```bash
# Запуск основного бота (требует настроенные токены)
python bot.py

# Запуск планировщика задач
python scheduler.py

# Тестирование Grok API
python -c "import asyncio; from grok_service import GrokService; asyncio.run(GrokService().generate_ai_topics('test'))"
```

## 📁 Структура проекта

```
my_ai_teacher_3/
├── 🤖 bot.py                 # Основной Telegram бот
├── 🧠 grok_service.py        # Интеграция с Grok API  
├── 🗄️ database.py           # Модели данных SQLAlchemy
├── 📚 topic_service.py       # Управление темами обучения
├── ⏰ scheduler.py           # Планировщик задач
├── 🏥 health_check.py        # Диагностика системы
├── 🐳 docker-compose.yml     # Docker конфигурация
├── 📋 requirements.txt       # Продакшн зависимости
├── 🔧 requirements-dev.txt   # Локальные зависимости
├── 🧪 test_simple.py         # Быстрый тест модулей
├── ⚙️ .env.local            # Локальная конфигурация
└── 📁 venv/                  # Виртуальная среда Python
```

## 🔧 Установленные пакеты

### Основные зависимости
- `python-telegram-bot==20.8` - Telegram Bot API
- `sqlalchemy==2.0.42` - ORM для работы с базой данных  
- `aiohttp==3.12.15` - Асинхронный HTTP клиент
- `requests==2.32.3` - HTTP запросы
- `beautifulsoup4==4.12.3` - Парсинг HTML
- `schedule==1.2.2` - Планировщик задач

### Инструменты разработки
- `ipython==8.30.0` - Улучшенная интерактивная оболочка
- `pytest==8.3.4` - Фреймворк для тестирования
- `black==24.10.0` - Форматирование кода
- `flake8==7.1.1` - Линтер кода

### ⚠️ Недоступно локально
- `psycopg2-binary` - требует Microsoft Visual C++ 14.0+
- `asyncpg` - требует компилятор C++

## 🎯 Возможности для разработки

### ✅ Доступно сейчас
- ✅ Импорт и тестирование всех модулей
- ✅ Работа с Grok API (при наличии ключа)
- ✅ Генерация AI контента и тем
- ✅ Telegram Bot интерфейс (при наличии токена)
- ✅ Планирование задач
- ✅ Логирование и диагностика
- ✅ Форматирование и линтинг кода

### ⚠️ Ограничения
- ❌ Подключение к PostgreSQL (нужен компилятор или Docker)
- ❌ Полное тестирование с базой данных
- ❌ Сохранение пользовательских данных

### 💡 Обходные решения
1. **Для тестирования без БД**: Используйте SQLite - раскомментируйте в `.env.local`:
   ```env
   DATABASE_URL=sqlite:///local_test.db
   ```

2. **Для полной функциональности**: Используйте Docker:
   ```bash
   docker-compose up -d
   ```

3. **Для установки PostgreSQL драйверов**: Установите Microsoft Build Tools for Visual Studio

## 📝 Полезные команды

### Проверка состояния
```bash
# Статус виртуальной среды
pip list

# Проверка модулей
python -c "import bot, grok_service, topic_service; print('Все модули загружены')"

# Тест конфигурации
python health_check.py
```

### Разработка
```bash
# Форматирование кода
black *.py

# Проверка стиля
flake8 *.py

# Интерактивная разработка
ipython
```

### Отладка
```bash
# Просмотр логов
Get-Content logs/scheduler.log -Tail 20

# Тест отдельного компонента
python -c "from grok_service import GrokService; print('GrokService готов')"
```

## 🎉 Следующие шаги

1. **Настройте токены** в `.env.local`
2. **Запустите тесты**: `python test_simple.py`  
3. **Начните разработку** с любого модуля
4. **Используйте Docker** для полного тестирования с базой данных

---

**Среда готова к разработке!** 🚀
