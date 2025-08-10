import os
import asyncio
import logging
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
from database import Database
from grok_service import GrokService
from topic_service import TopicService

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TopicScheduler:
    def __init__(self):
        self.db = Database()
        self.grok = GrokService()
        self.topic_service = TopicService(self.db, self.grok)

    async def update_topics_job(self):
        """Задача обновления тем"""
        try:
            logger.info("📅 Запуск еженедельного обновления тем...")
            await self.topic_service.update_all_topics()
            logger.info("✅ Темы успешно обновлены")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления тем: {e}")

    async def monitor_ai_news_job(self):
        """Задача мониторинга новостей ИИ"""
        try:
            logger.info("📰 Мониторинг новостей ИИ...")
            news = await self.grok.monitor_ai_news()
            
            if news:
                logger.info(f"📰 Найдено {len(news)} новостей по ИИ")
                # Здесь можно добавить логику отправки новостей администраторам
                
        except Exception as e:
            logger.error(f"❌ Ошибка мониторинга новостей: {e}")

    def run_async_job(self, job_func):
        """Обертка для запуска асинхронных задач"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(job_func())
        finally:
            loop.close()

    def setup_schedule(self):
        """Настройка расписания задач"""
        
        # Обновление тем каждую неделю в воскресенье в 03:00
        schedule.every().sunday.at("03:00").do(
            self.run_async_job, 
            self.update_topics_job
        )
        
        # Мониторинг новостей каждый день в 09:00
        schedule.every().day.at("09:00").do(
            self.run_async_job,
            self.monitor_ai_news_job
        )
        
        # Дополнительное обновление тем в среду в 15:00 (для актуальности)
        schedule.every().wednesday.at("15:00").do(
            self.run_async_job,
            self.update_topics_job
        )
        
        logger.info("📅 Расписание задач настроено:")
        logger.info("   • Обновление тем: воскресенье 03:00, среда 15:00")
        logger.info("   • Мониторинг новостей: ежедневно 09:00")

    async def init_scheduler(self):
        """Инициализация планировщика"""
        try:
            await self.db.init_db()
            await self.topic_service.initialize_topics()
            logger.info("✅ Планировщик инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации планировщика: {e}")
            return False

    def run(self):
        """Запуск планировщика"""
        logger.info("🕐 Запуск планировщика задач...")
        
        # Инициализация
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            init_success = loop.run_until_complete(self.init_scheduler())
            if not init_success:
                logger.error("❌ Не удалось инициализировать планировщик")
                return
            
            # Настройка расписания
            self.setup_schedule()
            
            # Запуск основного цикла
            while True:
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
                
        except KeyboardInterrupt:
            logger.info("👋 Планировщик остановлен")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка планировщика: {e}")
        finally:
            loop.close()

def main():
    """Главная функция"""
    # Создание директории для логов
    os.makedirs('logs', exist_ok=True)
    
    scheduler = TopicScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()
