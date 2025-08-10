#!/usr/bin/env python3
"""
Тест команды прогресса после исправления SQLAlchemy 2.0
"""
import asyncio
import logging
import os
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User as TelegramUser
from telegram.ext import ContextTypes

# Настраиваем путь и логирование
import sys
sys.path.append(os.getcwd())

from bot import AILearningBot

# Отключаем лишние логи
logging.basicConfig(level=logging.ERROR)

async def test_progress_command():
    """Тест команды /progress с исправленными методами базы данных"""
    
    print("🔧 Тестируем команду /progress после исправления SQLAlchemy...")
    
    # Создаем бота
    bot = AILearningBot()
    
    # Мокаем методы базы данных, чтобы они возвращали тестовые данные
    bot.db.get_user_stats = AsyncMock(return_value={
        'total_points': 250,
        'completed_topics': 3,
        'learning_days': 5,
        'streak': 2
    })
    
    bot.db.get_completed_topics = AsyncMock(return_value=[
        {'id': 1, 'title': 'Python Основы', 'completed_at': '2025-08-10', 'points_earned': 100},
        {'id': 2, 'title': 'Алгоритмы', 'completed_at': '2025-08-09', 'points_earned': 150}
    ])
    
    # Создаем mock update и context
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=TelegramUser)
    update.effective_user.id = 12345
    update.effective_user.first_name = "TestUser"
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    
    try:
        # Вызываем команду прогресса
        await bot.show_progress(update, context)
        
        # Проверяем, что методы базы данных были вызваны
        bot.db.get_user_stats.assert_called_once_with(12345)
        bot.db.get_completed_topics.assert_called_once_with(12345)
        
        # Проверяем, что сообщение было отправлено
        update.message.reply_text.assert_called_once()
        
        # Получаем текст сообщения
        sent_message = update.message.reply_text.call_args[0][0]
        
        print("✅ Команда /progress выполнена успешно!")
        print("📊 Отправленное сообщение:")
        print("-" * 50)
        print(sent_message)
        print("-" * 50)
        
        # Проверяем, что в сообщении есть ключевые элементы
        assert "📊 Ваш прогресс обучения" in sent_message
        assert "250 баллов" in sent_message
        assert "3 темы" in sent_message
        assert "5 дней" in sent_message
        assert "Python Основы" in sent_message
        
        print("✅ Все проверки прошли успешно - прогресс работает корректно!")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(test_progress_command())
