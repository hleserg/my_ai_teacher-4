# 🚀 Быстрый запуск AI Learning Bot

## Шаг 1: Подготовка
1. Убедитесь что установлен Docker и Docker Compose
2. Клонируйте проект или скачайте файлы

## Шаг 2: Создание Telegram бота
1. Напишите [@BotFather](https://t.me/botfather)
2. Отправьте `/newbot` и следуйте инструкциям  
3. Скопируйте полученный токен

## Шаг 3: Настройка
1. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Откройте `.env` и замените `your_telegram_bot_token_here` на ваш токен:
   ```
   TELEGRAM_BOT_TOKEN=1234567890:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

## Шаг 4: Запуск
```bash
docker-compose up -d
```

## Шаг 5: Проверка
1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Бот должен ответить приветствием

## 🔧 Полезные команды

```bash
# Просмотр логов
docker-compose logs -f bot

# Перезапуск
docker-compose restart

# Остановка
docker-compose down

# Полная очистка (удаляет данные!)
docker-compose down -v
```

## ❗ В случае проблем

1. Проверьте что Docker запущен
2. Убедитесь что токен бота правильный
3. Посмотрите логи: `docker-compose logs bot`

Готово! Ваш AI Learning Bot работает! 🎉
