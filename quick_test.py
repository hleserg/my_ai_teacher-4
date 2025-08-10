#!/usr/bin/env python3
"""
Быстрая проверка синтаксиса бота
"""
import os

os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///local_test.db'

try:
    from bot import AILearningBot
    print("✅ Импорт бота успешен")
    
    bot = AILearningBot()
    print("✅ Создание экземпляра бота успешно")
    
    print(f"✅ Метод handle_question_button: {hasattr(bot, 'handle_question_button')}")
    print(f"✅ Метод handle_question: {hasattr(bot, 'handle_question')}")
    
    # Проверим, что методы действительно вызываемые
    if hasattr(bot, 'handle_question_button'):
        print(f"✅ handle_question_button вызываемый: {callable(getattr(bot, 'handle_question_button'))}")
    
    print("\n🎯 Все методы с 'question' в названии:")
    for attr_name in dir(bot):
        if 'question' in attr_name.lower() and not attr_name.startswith('_'):
            print(f"  📌 {attr_name}")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
