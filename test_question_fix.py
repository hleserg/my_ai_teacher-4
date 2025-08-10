#!/usr/bin/env python3
"""
Тестирование исправления ошибки в handle_question
"""
import os
import asyncio

os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///local_test.db'

def test_method_availability():
    """Проверяем наличие методов для отправки сообщений"""
    try:
        from bot import AILearningBot
        print("✅ Импорт бота успешен")
        
        bot = AILearningBot()
        print("✅ Создание экземпляра бота успешно")
        
        # Проверяем наличие методов отправки сообщений
        methods_to_check = [
            '_send_long_message',
            '_send_long_text_message',
            'handle_question',
            'handle_question_button'
        ]
        
        print("\n🔧 Проверка методов отправки сообщений:")
        for method_name in methods_to_check:
            if hasattr(bot, method_name) and callable(getattr(bot, method_name)):
                print(f"  ✅ {method_name} - найден и вызываемый")
            else:
                print(f"  ❌ {method_name} - НЕ найден или не вызываемый")
        
        print("\n🧪 Анализируем сигнатуры методов:")
        
        if hasattr(bot, '_send_long_message'):
            import inspect
            sig = inspect.signature(bot._send_long_message)
            print(f"  📋 _send_long_message{sig}")
            
        if hasattr(bot, '_send_long_text_message'):
            import inspect
            sig = inspect.signature(bot._send_long_text_message)
            print(f"  📋 _send_long_text_message{sig}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_method_availability()
    if success:
        print("\n🎉 Все проверки пройдены! Методы для исправления ошибки доступны.")
    else:
        print("\n💥 Есть проблемы с методами.")
