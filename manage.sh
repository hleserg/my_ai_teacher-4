#!/bin/bash
# Скрипт команд для управления AI Learning Bot

echo "🤖 AI Learning Bot - Команды управления"
echo "=========================================="

case "$1" in
    "start")
        echo "🚀 Запуск всех сервисов..."
        docker-compose up -d
        ;;
    "stop")
        echo "⏹️ Остановка всех сервисов..."
        docker-compose down
        ;;
    "restart")
        echo "🔄 Перезапуск бота..."
        docker-compose restart bot
        ;;
    "logs")
        echo "📋 Просмотр логов бота..."
        docker-compose logs -f bot
        ;;
    "logs-all")
        echo "📋 Просмотр всех логов..."
        docker-compose logs -f
        ;;
    "status")
        echo "📊 Статус сервисов..."
        docker-compose ps
        ;;
    "health")
        echo "🏥 Проверка работоспособности..."
        python health_check.py
        ;;
    "update")
        echo "🔄 Обновление и пересборка..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    "clean")
        echo "🧹 Полная очистка (УДАЛЯЕТ ВСЕ ДАННЫЕ!)..."
        read -p "Вы уверены? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker system prune -f
        fi
        ;;
    "setup")
        echo "⚙️ Первоначальная настройка..."
        if [ ! -f .env ]; then
            cp .env.example .env
            echo "✅ Создан .env файл"
            echo "⚠️  ОБЯЗАТЕЛЬНО укажите TELEGRAM_BOT_TOKEN в .env файле!"
        else
            echo "⚠️  .env файл уже существует"
        fi
        ;;
    *)
        echo "Доступные команды:"
        echo ""
        echo "🚀 Основные команды:"
        echo "  ./manage.sh setup    - Первоначальная настройка"
        echo "  ./manage.sh start    - Запуск всех сервисов"
        echo "  ./manage.sh stop     - Остановка всех сервисов"
        echo "  ./manage.sh restart  - Перезапуск бота"
        echo ""
        echo "📊 Мониторинг:"
        echo "  ./manage.sh status   - Статус сервисов"
        echo "  ./manage.sh logs     - Логи бота"
        echo "  ./manage.sh logs-all - Все логи"
        echo "  ./manage.sh health   - Проверка здоровья"
        echo ""
        echo "🔧 Обслуживание:"
        echo "  ./manage.sh update   - Обновление и пересборка"
        echo "  ./manage.sh clean    - Полная очистка"
        echo ""
        echo "📚 Быстрый старт:"
        echo "  1. ./manage.sh setup"
        echo "  2. Отредактируйте .env файл"
        echo "  3. ./manage.sh start"
        echo "  4. ./manage.sh logs"
        ;;
esac
