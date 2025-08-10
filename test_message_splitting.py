#!/usr/bin/env python3
"""
Тест разбивки длинных сообщений
"""
import os
import sys

# Устанавливаем переменные окружения
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///local_test.db'

try:
    from bot import AILearningBot
    print("✅ Импорт бота успешен")
    
    bot = AILearningBot()
    print("✅ Создание экземпляра бота успешно")
    
    # Проверяем методы разбивки сообщений
    methods_to_check = [
        '_split_long_message',
        '_send_long_message', 
        '_send_long_text_message'
    ]
    
    for method_name in methods_to_check:
        if hasattr(bot, method_name) and callable(getattr(bot, method_name)):
            print(f"✅ {method_name} - найден и вызываемый")
        else:
            print(f"❌ {method_name} - НЕ найден или не вызываемый")
    
    # Тестируем разбивку длинного текста
    print("\n🧪 Тестируем разбивку длинного текста:")
    long_text = "**📖 Тестовая тема**\n\n" + "Это очень длинный текст. " * 300  # Примерно 7500 символов
    
    parts = bot._split_long_message(long_text)
    print(f"📄 Исходный текст: {len(long_text)} символов")
    print(f"📄 Разбито на {len(parts)} частей")
    
    for i, part in enumerate(parts, 1):
        print(f"📄 Часть {i}: {len(part)} символов (лимит: 4096)")
        if len(part) > 4096:
            print(f"❌ Часть {i} превышает лимит!")
        else:
            print(f"✅ Часть {i} в пределах лимита")
    
    print("\n🎉 Тест разбивки сообщений завершен!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
