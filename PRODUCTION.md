# 🚀 Развертывание AI Learning Bot в продакшене

Полное руководство по развертыванию AI Learning Bot с использованием Docker Compose в продакшен среде.

## 📋 Требования

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Минимум 1GB RAM** на сервере
- **Минимум 10GB дискового пространства**
- **Telegram Bot Token** (от @BotFather)
- **Grok API Key** (для генерации контента)

## 🎯 Быстрый старт

### 1. Подготовка сервера
```bash
# Обновление системы (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt install docker-compose-plugin -y
```

### 2. Клонирование и настройка
```bash
# Клонирование репозитория
git clone <repository_url>
cd my_ai_teacher

# Создание конфигурации
cp .env.prod.example .env.prod
nano .env.prod  # Заполните все переменные
```

**Обязательные переменные:**
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
GROK_API_KEY=your_grok_api_key_here
POSTGRES_PASSWORD=secure_password_123
REDIS_PASSWORD=secure_redis_password_123
```

### 3. Развертывание

#### Автоматическое развертывание:
```bash
# Linux/macOS
chmod +x deploy.sh
./deploy.sh production

# Windows PowerShell
.\deploy.ps1 production
```

#### Ручное развертывание:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## 🛠 Компоненты системы

### Основные сервисы:
- **bot** - Telegram бот (Python + python-telegram-bot)
- **scheduler** - Планировщик обновления тем  
- **db** - База данных PostgreSQL 15
- **redis** - Кеширование и сессии

### Опциональные сервисы:
- **prometheus** - Сбор метрик (профиль monitoring)
- **grafana** - Визуализация метрик (профиль monitoring)

## 📊 Мониторинг

### Запуск с мониторингом:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod --profile monitoring up -d
```

### Доступ к панелям:
- **Grafana**: http://your-server:3000
  - Логин: `admin`
  - Пароль: из `GRAFANA_PASSWORD`
- **Prometheus**: http://your-server:9090

## 🔧 Управление

### Просмотр статуса:
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Логи сервисов:
```bash
# Все логи
docker-compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f bot
docker-compose -f docker-compose.prod.yml logs -f scheduler
docker-compose -f docker-compose.prod.yml logs -f db
```

### Перезапуск:
```bash
# Все сервисы
docker-compose -f docker-compose.prod.yml restart

# Конкретный сервис
docker-compose -f docker-compose.prod.yml restart bot
```

### Обновление кода:
```bash
# Остановка
docker-compose -f docker-compose.prod.yml down

# Обновление кода
git pull

# Пересборка и запуск
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

## 🗄️ Резервное копирование

### База данных:
```bash
# Создание бэкапа
docker-compose -f docker-compose.prod.yml exec db pg_dump -U ai_bot ai_learning > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление
docker-compose -f docker-compose.prod.yml exec -T db psql -U ai_bot ai_learning < backup_file.sql
```

### Конфигурация и логи:
```bash
# Архив важных файлов
tar -czf ai_learning_backup_$(date +%Y%m%d).tar.gz \
    .env.prod \
    docker-compose.prod.yml \
    logs/ \
    config/
```

## 🔒 Безопасность

### Обязательные шаги:
1. **Измените все пароли** в `.env.prod`
2. **Закройте неиспользуемые порты** в firewall
3. **Настройте SSL/TLS** для публичного доступа
4. **Регулярно обновляйте** Docker образы

### Настройка firewall (Ubuntu):
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80    # HTTP (если нужен)
sudo ufw allow 443   # HTTPS (если нужен)
sudo ufw allow 3000  # Grafana (если нужен внешний доступ)
```

## 🐛 Диагностика

### Проверка работоспособности:
```bash
# Диагностика системы
docker-compose -f docker-compose.prod.yml exec bot python health_check.py

# Проверка подключения к Telegram
docker-compose -f docker-compose.prod.yml exec bot python -c "
import os, requests
token = os.getenv('TELEGRAM_BOT_TOKEN')
r = requests.get(f'https://api.telegram.org/bot{token}/getMe')
print('Bot status:', r.json().get('ok', False))
"
```

### Частые проблемы:

#### Бот не отвечает:
1. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs bot`
2. Убедитесь в корректности `TELEGRAM_BOT_TOKEN`
3. Проверьте, не запущен ли бот в другом месте

#### Ошибки базы данных:
1. Проверьте статус: `docker-compose -f docker-compose.prod.yml exec db pg_isready`
2. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs db`
3. Убедитесь в корректности `POSTGRES_PASSWORD`

#### Высокое потребление ресурсов:
1. Мониторинг: `docker stats`
2. Увеличьте лимиты в `docker-compose.prod.yml`
3. Добавьте swap: `sudo fallocate -l 2G /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`

## 📈 Масштабирование

### Горизонтальное масштабирование:
```bash
# Увеличение количества экземпляров бота
docker-compose -f docker-compose.prod.yml up -d --scale bot=3
```

### Оптимизация производительности:
- Увеличьте `shared_buffers` в PostgreSQL
- Настройте connection pooling
- Используйте Redis для кеширования

## 🌍 Переменные окружения

| Переменная | Описание | Обязательная | По умолчанию |
|------------|----------|-------------|-------------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | ✅ | - |
| `GROK_API_KEY` | API ключ Grok | ✅ | - |
| `POSTGRES_DB` | Имя БД | ❌ | ai_learning |
| `POSTGRES_USER` | Пользователь БД | ❌ | ai_bot |
| `POSTGRES_PASSWORD` | Пароль БД | ✅ | - |
| `REDIS_PASSWORD` | Пароль Redis | ✅ | - |
| `LOG_LEVEL` | Уровень логирования | ❌ | INFO |
| `TIMEZONE` | Часовой пояс | ❌ | Europe/Moscow |

## ✅ Готово!

После успешного развертывания:

1. **Проверьте статус**: `docker-compose -f docker-compose.prod.yml ps`
2. **Протестируйте бота**: отправьте `/start` в Telegram
3. **Настройте мониторинг**: откройте Grafana при необходимости
4. **Настройте резервное копирование**: создайте cron задачи

Ваш AI Learning Bot готов к работе! 🚀
