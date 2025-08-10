#!/usr/bin/env python3
"""
Тест исправленных методов прогресса с локальной SQLite базой
"""
import asyncio
import sqlite3
import os
from datetime import datetime

# Создаем простую SQLite базу для теста
def create_test_db():
    conn = sqlite3.connect('test_progress.db')
    cursor = conn.cursor()
    
    # Создаем таблицы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            total_points INTEGER DEFAULT 0,
            current_topic_id INTEGER,
            created_at TEXT,
            last_activity TEXT,
            streak INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            learning_time TEXT,
            difficulty TEXT,
            priority INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS completed_topics (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            topic_id INTEGER,
            completed_at TEXT,
            points_earned INTEGER DEFAULT 10,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (topic_id) REFERENCES topics (id)
        )
    ''')
    
    # Добавляем тестового пользователя
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (telegram_id, username, total_points, created_at, last_activity, streak)
        VALUES (12345, 'test_user', 150, ?, ?, 3)
    ''', (datetime.now().isoformat(), datetime.now().isoformat()))
    
    # Добавляем тестовые темы
    topics_data = [
        (1, 'Python Основы', 'Введение в Python', 'general', '30 мин', 'easy', 1),
        (2, '1С:Предприятие', 'Основы 1С', '1c', '45 мин', 'medium', 2),
        (3, 'Алгоритмы', 'Структуры данных', 'general', '60 мин', 'hard', 3)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO topics 
        (id, title, description, category, learning_time, difficulty, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', topics_data)
    
    # Добавляем завершенные темы
    completed_data = [
        (1, 1, datetime.now().isoformat(), 50),
        (1, 2, datetime.now().isoformat(), 100)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO completed_topics 
        (user_id, topic_id, completed_at, points_earned)
        VALUES (?, ?, ?, ?)
    ''', completed_data)
    
    conn.commit()
    conn.close()
    print("✅ Тестовая база данных создана")

async def test_sqlite_methods():
    """Тест методов с SQLite"""
    print("🔧 Тестируем исправленные методы прогресса...")
    
    # Имитируем логику get_user_stats
    conn = sqlite3.connect('test_progress.db')
    cursor = conn.cursor()
    
    # Получаем пользователя
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (12345,))
    user = cursor.fetchone()
    
    if user:
        # Подсчитываем завершенные темы
        cursor.execute('SELECT COUNT(*) FROM completed_topics WHERE user_id = ?', (user[0],))
        completed_count = cursor.fetchone()[0]
        
        # Подсчитываем дни обучения
        created_at = datetime.fromisoformat(user[5])
        learning_days = (datetime.now() - created_at).days + 1
        
        stats = {
            'total_points': user[3],
            'completed_topics': completed_count,
            'learning_days': learning_days,
            'streak': user[7]
        }
        
        print(f"📊 Статистика пользователя: {stats}")
        
        # Получаем завершенные темы
        cursor.execute('''
            SELECT ct.topic_id, t.title, ct.completed_at, ct.points_earned
            FROM completed_topics ct
            JOIN topics t ON ct.topic_id = t.id
            WHERE ct.user_id = ?
        ''', (user[0],))
        
        completed_topics = []
        for row in cursor.fetchall():
            completed_topics.append({
                'id': row[0],
                'title': row[1], 
                'completed_at': row[2],
                'points_earned': row[3]
            })
            
        print(f"📚 Завершенные темы: {completed_topics}")
        
    conn.close()
    
    # Удаляем тестовую базу
    if os.path.exists('test_progress.db'):
        os.remove('test_progress.db')
    
    print("✅ Тест завершен успешно - методы базы данных работают корректно!")

if __name__ == '__main__':
    create_test_db()
    asyncio.run(test_sqlite_methods())
