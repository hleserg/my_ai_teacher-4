import asyncio
import sqlite3
import os
from dotenv import load_dotenv
from grok_service import GrokService

# Загружаем переменные окружения
load_dotenv()
if os.path.exists('.env.local'):
    load_dotenv('.env.local', override=True)

async def regenerate_topics():
    """Очистить и заново сгенерировать темы на русском языке"""
    
    # Очищаем существующие темы
    conn = sqlite3.connect('local_test.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM topics')
    conn.commit()
    conn.close()
    print("✅ Очистили все существующие темы")
    
    # Генерируем новые темы на русском
    grok = GrokService()
    topics = await grok.generate_ai_topics("general")
    
    if topics:
        # Сохраняем в базу
        conn = sqlite3.connect('local_test.db')
        cursor = conn.cursor()
        
        for topic in topics:
            cursor.execute("""
                INSERT INTO topics (title, description, category, learning_time, difficulty, priority, is_active, created_at, updated_at)
                VALUES (?, ?, 'general', ?, ?, ?, 1, datetime('now'), datetime('now'))
            """, (
                topic.get('title', ''),
                topic.get('description', ''),
                topic.get('learning_time', '1-3 дня'),
                topic.get('difficulty', 'Средний'),
                topic.get('priority', 10)
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ Сгенерировано и сохранено {len(topics)} новых тем на русском языке")
        
        # Покажем первые 3 темы
        conn = sqlite3.connect('local_test.db')
        cursor = conn.cursor()
        cursor.execute('SELECT title, description FROM topics LIMIT 3')
        new_topics = cursor.fetchall()
        conn.close()
        
        print("\nПервые 3 новые темы:")
        for i, (title, desc) in enumerate(new_topics, 1):
            print(f"{i}. {title}")
            print(f"   {desc[:100]}...")
            print()
    else:
        print("❌ Не удалось сгенерировать темы")

if __name__ == "__main__":
    asyncio.run(regenerate_topics())
