#!/usr/bin/env python3
"""
Тестовый скрипт для локальной разработки
Позволяет протестировать основные компоненты без запуска полного бота
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

async def test_grok_service():
    """Тестируем GrokService"""
    try:
        from grok_service import GrokService
        
        print("🔧 Тестируем GrokService...")
        
        # Проверяем, что API ключ установлен
        api_key = os.getenv('GROK_API_KEY')
        if not api_key or api_key == 'your_grok_api_key_here':
            print("❌ GROK_API_KEY не установлен или имеет тестовое значение")
            return False
        
        grok = GrokService()
        
        # Простой тест генерации контента
        test_topic = {
            'title': 'Машинное обучение',
            'description': 'Основы машинного обучения',
            'difficulty': 'beginner'
        }
        
        print("   Генерируем тестовый контент...")
        content = await grok.generate_content(test_topic)
        
        if content and len(content) > 50:
            print("✅ GrokService работает корректно")
            print(f"   Сгенерировано символов: {len(content)}")
            return True
        else:
            print("❌ GrokService вернул пустой или слишком короткий контент")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании GrokService: {e}")
        return False

async def test_topic_service():
    """Тестируем TopicService"""
    try:
        from topic_service import TopicService
        
        print("🔧 Тестируем TopicService...")
        
        topic_service = TopicService()
        
        # Тестируем получение топиков
        topics = await topic_service.get_topics_by_difficulty('beginner')
        
        if topics and len(topics) > 0:
            print(f"✅ TopicService работает корректно")
            print(f"   Найдено топиков для начинающих: {len(topics)}")
            return True
        else:
            print("❌ TopicService не вернул топики")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании TopicService: {e}")
        return False

def test_imports():
    """Тестируем импорты всех модулей"""
    modules = [
        'grok_service',
        'topic_service', 
        'database',
        'bot',
        'scheduler',
        'health_check'
    ]
    
    print("🔧 Тестируем импорты модулей...")
    
    success_count = 0
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"   ❌ {module_name}: {e}")
    
    print(f"Успешно импортировано: {success_count}/{len(modules)} модулей")
    return success_count == len(modules)

async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов локальной разработки")
    print("=" * 50)
    
    # Загружаем переменные окружения из .env.local если файл существует
    env_local_path = Path('.env.local')
    if env_local_path.exists():
        print("📁 Загружаем .env.local")
        with open(env_local_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print("⚠️  Файл .env.local не найден, используем системные переменные")
    
    print()
    
    # Тестируем импорты
    imports_ok = test_imports()
    print()
    
    # Тестируем TopicService (не требует API ключей)
    topic_service_ok = await test_topic_service()
    print()
    
    # Тестируем GrokService (требует API ключ)
    grok_service_ok = await test_grok_service()
    print()
    
    # Итоги
    print("=" * 50)
    print("📊 Результаты тестирования:")
    print(f"   Импорты: {'✅' if imports_ok else '❌'}")
    print(f"   TopicService: {'✅' if topic_service_ok else '❌'}")  
    print(f"   GrokService: {'✅' if grok_service_ok else '❌'}")
    print()
    
    if imports_ok and topic_service_ok:
        print("🎉 Базовая функциональность готова к разработке!")
        if not grok_service_ok:
            print("💡 Настройте GROK_API_KEY в .env.local для полного тестирования")
    else:
        print("🔧 Необходимо устранить ошибки перед началом разработки")

if __name__ == "__main__":
    asyncio.run(main())
