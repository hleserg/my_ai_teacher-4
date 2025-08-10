import os
import logging
from dotenv import load_dotenv
from bot import AILearningBot

# Настройка логирования (до загрузки переменных)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Временно только в консоль
    ]
)

logger = logging.getLogger(__name__)

# Загрузка переменных окружения
# Сначала загружаем .env, затем .env.local (приоритет у local)
load_dotenv()
if os.path.exists('.env.local'):
    load_dotenv('.env.local', override=True)
    logger.info("📁 Загружены переменные из .env.local")

# Создание директории для логов и добавление файлового логгера
os.makedirs('logs', exist_ok=True)
file_handler = logging.FileHandler('logs/bot.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

def main():
    """Основная функция"""
    logger.info("🚀 Запуск AI Learning Bot...")
    
    # Проверка токена
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not telegram_token or telegram_token == 'YOUR_TELEGRAM_BOT_TOKEN':
        logger.error("❌ Не установлен TELEGRAM_BOT_TOKEN!")
        logger.error("Создайте .env файл и добавьте туда:")
        logger.error("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return
    
    try:
        # Создаем и запускаем бота (он сам инициализирует сервисы)
        bot = AILearningBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()
