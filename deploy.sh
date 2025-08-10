#!/bin/bash
# Скрипт быстрого развертывания AI Learning Bot в продакшене
# 
# Использование:
# chmod +x deploy.sh
# ./deploy.sh [development|production|monitoring]

set -e  # Остановить выполнение при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка аргументов
MODE=${1:-production}

log_info "🚀 Развертывание AI Learning Bot в режиме: $MODE"

# Проверка Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker не установлен. Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose не установлен. Установите Docker Compose"
    exit 1
fi

# Проверка файлов конфигурации
case $MODE in
    "development")
        COMPOSE_FILE="docker-compose.yml"
        ENV_FILE=".env.local"
        ;;
    "production")
        COMPOSE_FILE="docker-compose.prod.yml" 
        ENV_FILE=".env.prod"
        ;;
    "monitoring")
        COMPOSE_FILE="docker-compose.prod.yml"
        ENV_FILE=".env.prod"
        PROFILES="--profile monitoring"
        ;;
    *)
        log_error "Неизвестный режим: $MODE. Используйте: development, production, monitoring"
        exit 1
        ;;
esac

# Проверка существования файлов
if [[ ! -f "$COMPOSE_FILE" ]]; then
    log_error "Файл $COMPOSE_FILE не найден!"
    exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
    log_warning "Файл $ENV_FILE не найден. Создаем из примера..."
    
    if [[ "$MODE" == "production" || "$MODE" == "monitoring" ]]; then
        if [[ -f ".env.prod.example" ]]; then
            cp .env.prod.example "$ENV_FILE"
            log_info "Файл $ENV_FILE создан из .env.prod.example"
            log_warning "⚠️  ВАЖНО: Отредактируйте $ENV_FILE и заполните все переменные!"
            read -p "Нажмите Enter после редактирования файла..."
        else
            log_error "Файл .env.prod.example не найден!"
            exit 1
        fi
    fi
fi

# Проверка обязательных переменных
log_info "🔍 Проверка конфигурации..."

if grep -q "your_telegram_bot_token_here\|your_grok_api_key_here" "$ENV_FILE" 2>/dev/null; then
    log_error "В файле $ENV_FILE есть незаполненные переменные. Проверьте конфигурацию!"
    exit 1
fi

# Создание необходимых директорий
log_info "📁 Создание директорий..."
mkdir -p logs config ssl nginx/logs monitoring/grafana/provisioning

# Остановка существующих контейнеров
log_info "🛑 Остановка существующих контейнеров..."
docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true

# Сборка образов
log_info "🔨 Сборка Docker образов..."
docker-compose -f "$COMPOSE_FILE" build --no-cache

# Запуск сервисов
log_info "🚀 Запуск сервисов..."

if [[ "$MODE" == "monitoring" ]]; then
    log_info "Запуск с профилем мониторинга..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" $PROFILES up -d
else
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
fi

# Ожидание запуска
log_info "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
log_info "📊 Статус сервисов:"
docker-compose -f "$COMPOSE_FILE" ps

# Проверка здоровья
log_info "🔍 Проверка работоспособности..."
sleep 15

if docker-compose -f "$COMPOSE_FILE" exec -T bot python health_check.py; then
    log_success "✅ Система работает корректно!"
else
    log_warning "⚠️  Проблемы с работоспособностью системы"
fi

# Информация о запущенных сервисах
log_success "🎉 Развертывание завершено!"
echo ""
log_info "📋 Полезные команды:"
echo "  Логи бота:           docker-compose -f $COMPOSE_FILE logs -f bot"
echo "  Логи планировщика:   docker-compose -f $COMPOSE_FILE logs -f scheduler"
echo "  Статус сервисов:     docker-compose -f $COMPOSE_FILE ps"
echo "  Остановка:           docker-compose -f $COMPOSE_FILE down"
echo "  Перезапуск:          docker-compose -f $COMPOSE_FILE restart"

if [[ "$MODE" == "monitoring" ]]; then
    echo ""
    log_info "🔗 Ссылки для мониторинга:"
    echo "  Grafana:    http://localhost:3000 (admin/admin123)"
    echo "  Prometheus: http://localhost:9090"
fi

echo ""
log_info "📝 Логи находятся в директории: ./logs/"
log_info "⚙️  Конфигурация: $ENV_FILE"

# Итоговая проверка
if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    log_success "🚀 AI Learning Bot успешно развернут и работает!"
else
    log_error "❌ Проблемы с запуском. Проверьте логи: docker-compose -f $COMPOSE_FILE logs"
    exit 1
fi
