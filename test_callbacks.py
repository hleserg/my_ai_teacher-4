#!/usr/bin/env python3
"""Тест обработчиков callback-ов для кнопок категорий"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

# Настройка переменных окружения
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///local_test.db'

def load_env_local():
    """Загружаем переменные из .env.local"""
    env_local_path = Path('.env.local')
    if env_local_path.exists():
        with open(env_local_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

async def test_callback_handlers():
    print("🧪 Тестирование обработчиков callback-ов...")
    
    # Загружаем переменные окружения
    load_env_local()
    
    try:
        from bot import AILearningBot
        
        # Создаем экземпляр бота
        bot = AILearningBot()
        print("✅ Бот создан успешно")
        
        # Проверяем, что обработчики существуют
        print("\n📋 Проверка наличия обработчиков:")
        
        handlers = [
            'show_general_topics_callback',
            'show_1c_topics_callback', 
            '_show_topics_list_callback',
            'back_to_topics'
        ]
        
        for handler_name in handlers:
            if hasattr(bot, handler_name):
                handler = getattr(bot, handler_name)
                if callable(handler):
                    print(f"   ✅ {handler_name} - найден и вызываемый")
                else:
                    print(f"   ❌ {handler_name} - найден, но не вызываемый")
            else:
                print(f"   ❌ {handler_name} - не найден")
        
        # Проверяем получение тем
        print("\n📚 Проверка получения тем:")
        
        try:
            general_topics = await bot.topic_service.get_topics_by_category("general")
            print(f"   ✅ Общие темы: {len(general_topics)} шт.")
            
            c1_topics = await bot.topic_service.get_topics_by_category("1c") 
            print(f"   ✅ Темы 1C: {len(c1_topics)} шт.")
            
        except Exception as e:
            print(f"   ❌ Ошибка получения тем: {e}")
        
        print("\n🎉 Тестирование завершено!")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_callback_handlers())
