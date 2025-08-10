#!/usr/bin/env python3
"""
Скрипт для ручного обновления тем
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('.env.local')
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from topic_service import TopicService
from grok_service import GrokService

async def update_topics():
    """Обновляет все темы"""
    
    print("🚀 Запуск обновления тем...")
    
    # Инициализируем сервисы
    db = Database()
    await db.init_db()
    
    grok_service = GrokService()
    topic_service = TopicService(db, grok_service)
    
    try:
        # Обновляем общие темы
        print("📚 Обновляем общие темы по ИИ...")
        await topic_service._generate_and_save_topics("general")
        print("✅ Общие темы обновлены")
        
        # Обновляем темы 1C
        print("🏢 Обновляем темы ИИ для 1C Enterprise...")
        await topic_service._generate_and_save_topics("1c")
        print("✅ Темы 1C обновлены")
        
        print("🎉 Все темы успешно обновлены!")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении тем: {e}")

if __name__ == "__main__":
    asyncio.run(update_topics())
