import os
import asyncio
import logging
from dotenv import load_dotenv
from bot_v13 import AILearningBot
from database import Database
from topic_service import TopicService
from grok_service import GrokService

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

async def init_services():
    """Инициализация всех сервисов"""
    try:
        # Инициализация базы данных
        db = Database()
        await db.init_db()
        logger.info("✅ База данных инициализирована")
        
        # Инициализация сервисов
        grok_service = GrokService()
        topic_service = TopicService(db, grok_service)
        
        # Инициализация тем при первом запуске
        await topic_service.initialize_topics()
        logger.info("✅ Темы инициализированы")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации сервисов: {e}")
        return False

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
        # Инициализируем сервисы асинхронно
        init_success = asyncio.run(init_services())
        if not init_success:
            logger.error("❌ Не удалось инициализировать сервисы")
            return
        
        logger.info("🤖 Бот готов к работе!")
        
        # Создаем и запускаем бота (синхронно для v13)
        bot = AILearningBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()
