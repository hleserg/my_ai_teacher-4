#!/usr/bin/env python3
"""
Тестирование обработчика кнопки "Задать вопрос"
"""
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import AILearningBot

def test_question_button_handler():
    """Тестирование наличия обработчика кнопки вопроса"""
    print("🧪 Тестируем обработчик кнопки 'Задать вопрос'...")
    
    try:
        bot = AILearningBot()
        
        # Проверяем, что метод handle_question_button существует и вызываемый
        if hasattr(bot, 'handle_question_button') and callable(getattr(bot, 'handle_question_button')):
            print("✅ handle_question_button - найден и вызываемый")
        else:
            print("❌ handle_question_button - НЕ найден или не вызываемый")
            
        # Проверяем обновленный метод handle_question
        if hasattr(bot, 'handle_question') and callable(getattr(bot, 'handle_question')):
            print("✅ handle_question - найден и вызываемый")
        else:
            print("❌ handle_question - НЕ найден или не вызываемый")
            
        print("\n🔧 Структура методов бота:")
        question_methods = [method for method in dir(bot) if 'question' in method.lower()]
        for method in question_methods:
            if not method.startswith('_'):
                print(f"  📌 {method}")
                
    except Exception as e:
        print(f"❌ Ошибка при создании бота: {e}")

if __name__ == "__main__":
    test_question_button_handler()
