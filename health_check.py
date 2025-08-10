#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности AI Learning Bot
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import Database
    from grok_service import GrokService  
    from topic_service import TopicService
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    print("Убедитесь что установлены все зависимости: pip install -r requirements.txt")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemHealthCheck:
    def __init__(self):
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Записать результат теста"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f": {message}"
        
        print(result)
        self.results.append((test_name, success, message))
        
    async def check_environment_variables(self):
        """Проверка переменных окружения"""
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        grok_key = os.getenv('GROK_API_KEY')
        
        if not telegram_token or telegram_token == 'your_telegram_bot_token_here':
            self.log_result("Environment Variables", False, "TELEGRAM_BOT_TOKEN не установлен")
            return False
            
        if len(telegram_token.split(':')) != 2:
            self.log_result("Environment Variables", False, "Неверный формат TELEGRAM_BOT_TOKEN")  
            return False
            
        self.log_result("Environment Variables", True, "Все переменные окружения настроены")
        return True
        
    async def check_database_connection(self):
        """Проверка подключения к базе данных"""
        try:
            db = Database()
            await db.init_db()
            self.log_result("Database Connection", True, "Подключение к БД установлено")
            return True
            
        except Exception as e:
            self.log_result("Database Connection", False, str(e))
            return False
            
    async def check_grok_api(self):
        """Проверка Grok API"""
        try:
            grok = GrokService()
            
            # Простая проверка API
            test_topics = await grok.generate_ai_topics("general")
            
            if test_topics and len(test_topics) > 0:
                self.log_result("Grok API", True, f"API работает, получено {len(test_topics)} тем")
                return True
            else:
                self.log_result("Grok API", False, "API не вернул данные")
                return False
                
        except Exception as e:
            self.log_result("Grok API", False, str(e))
            return False
            
    async def check_topic_service(self):
        """Проверка сервиса тем"""
        try:
            db = Database()
            grok = GrokService()
            topic_service = TopicService(db, grok)
            
            # Инициализация тем
            await topic_service.initialize_topics()
            
            # Получение тем
            topics = await topic_service.get_topics_by_category("general")
            
            if topics and len(topics) > 0:
                self.log_result("Topic Service", True, f"Сервис работает, найдено {len(topics)} тем")
                return True
            else:
                self.log_result("Topic Service", False, "Не удалось получить темы")
                return False
                
        except Exception as e:
            self.log_result("Topic Service", False, str(e))
            return False
            
    async def check_docker_environment(self):
        """Проверка Docker окружения"""
        # Проверяем, запущен ли бот в контейнере
        if os.path.exists('/.dockerenv'):
            self.log_result("Docker Environment", True, "Запущено в Docker контейнере")
            return True
        else:
            self.log_result("Docker Environment", True, "Запущено локально")
            return True
            
    async def run_all_checks(self):
        """Запуск всех проверок"""
        print("🔍 Проверка работоспособности AI Learning Bot")
        print(f"⏰ Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        checks = [
            self.check_environment_variables,
            self.check_docker_environment,
            self.check_database_connection, 
            self.check_grok_api,
            self.check_topic_service
        ]
        
        passed = 0
        total = len(checks)
        
        for check in checks:
            try:
                result = await check()
                if result:
                    passed += 1
            except Exception as e:
                logger.error(f"Ошибка при выполнении проверки {check.__name__}: {e}")
                
        print("=" * 60)
        print(f"📊 Результат: {passed}/{total} проверок пройдено")
        
        if passed == total:
            print("🎉 Все проверки прошли успешно! Бот готов к работе!")
            return True
        else:
            print(f"⚠️  {total - passed} проверок не прошли. Исправьте ошибки перед запуском.")
            return False
            
    def print_recommendations(self):
        """Рекомендации по устранению проблем"""
        failed_tests = [r for r in self.results if not r[1]]
        
        if not failed_tests:
            return
            
        print("\n🔧 Рекомендации по устранению проблем:")
        print("-" * 50)
        
        for test_name, _, message in failed_tests:
            if "TELEGRAM_BOT_TOKEN" in message:
                print("• Создайте .env файл и добавьте корректный TELEGRAM_BOT_TOKEN")
                print("• Получить токен можно у @BotFather в Telegram")
                
            elif "Database" in test_name:
                print("• Убедитесь что PostgreSQL запущен")  
                print("• Для Docker: docker-compose up -d db")
                print("• Проверьте DATABASE_URL в .env файле")
                
            elif "Grok API" in test_name:
                print("• Проверьте интернет соединение")
                print("• Убедитесь что GROK_API_KEY корректный")
                print("• Возможны ограничения API (rate limits)")

async def main():
    """Главная функция"""
    # Загружаем переменные окружения из .env файла
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv не установлен, переменные окружения должны быть установлены вручную")
    
    # Создаем и запускаем проверки
    health_check = SystemHealthCheck()
    success = await health_check.run_all_checks()
    
    if not success:
        health_check.print_recommendations()
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
