#!/usr/bin/env python3
"""
Упрощенный тест для проверки основных компонентов
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

def load_env_local():
    """Загружаем переменные из .env.local"""
    env_local_path = Path('.env.local')
    if env_local_path.exists():
        print("📁 Загружаем .env.local")
        with open(env_local_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        return True
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
    
    print(f"Результат: {success_count}/{len(modules)} модулей импортировано успешно")
    return success_count == len(modules)

async def test_grok_methods():
    """Тестируем доступные методы GrokService"""
    try:
        from grok_service import GrokService
        
        print("🔧 Проверяем методы GrokService...")
        
        grok = GrokService()
        
        # Проверяем доступные методы
        methods = [m for m in dir(grok) if not m.startswith('_') and callable(getattr(grok, m))]
        print(f"   Доступные методы: {', '.join(methods)}")
        
        # Проверяем API ключ
        api_key = os.getenv('GROK_API_KEY')
        if not api_key or api_key == 'your_grok_api_key_here':
            print("   ⚠️  GROK_API_KEY не установлен - тестирование API пропущено")
            return True
        
        # Тестируем генерацию тем
        print("   Тестируем generate_ai_topics...")
        topics = await grok.generate_ai_topics("machine_learning")
        
        if topics and len(topics) > 0:
            print(f"   ✅ Сгенерировано {len(topics)} топиков")
            return True
        else:
            print("   ❌ Не удалось сгенерировать топики")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

async def main():
    """Главная функция"""
    print("🚀 Быстрый тест локальной разработки")
    print("=" * 50)
    
    # Загружаем локальные переменные
    env_loaded = load_env_local()
    if not env_loaded:
        print("⚠️  Файл .env.local не найден")
    print()
    
    # Тестируем импорты
    imports_ok = test_imports()
    print()
    
    # Тестируем GrokService
    grok_ok = await test_grok_methods()
    print()
    
    # Итоги
    print("=" * 50)
    print("📊 Итоги:")
    print(f"   Импорты: {'✅' if imports_ok else '❌'}")
    print(f"   GrokService: {'✅' if grok_ok else '❌'}")
    
    if imports_ok:
        print("\n🎉 Среда разработки готова!")
        print("💡 Для полного тестирования настройте GROK_API_KEY в .env.local")
        print("\n📝 Доступные команды для разработки:")
        print("   python health_check.py  - полная диагностика")
        print("   python bot.py          - запуск бота (требует токен)")
    else:
        print("\n🔧 Исправьте ошибки импорта перед разработкой")

if __name__ == "__main__":
    asyncio.run(main())
