import asyncio
import sqlite3
import os
from dotenv import load_dotenv
from grok_service import GrokService

# Загружаем переменные окружения
load_dotenv()
if os.path.exists('.env.local'):
    load_dotenv('.env.local', override=True)

async def regenerate_1c_topics():
    """Сгенерировать темы по 1C на русском языке"""
    
    # Удаляем существующие темы 1C
    conn = sqlite3.connect('local_test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM topics WHERE category = '1c'")
    conn.commit()
    conn.close()
    print("✅ Очистили существующие темы 1C")
    
    # Генерируем новые темы 1C на русском
    grok = GrokService()
    topics = await grok.generate_ai_topics("1c")
    
    if topics:
        # Сохраняем в базу
        conn = sqlite3.connect('local_test.db')
        cursor = conn.cursor()
        
        for topic in topics:
            cursor.execute("""
                INSERT INTO topics (title, description, category, learning_time, difficulty, priority, is_active, created_at, updated_at)
                VALUES (?, ?, '1c', ?, ?, ?, 1, datetime('now'), datetime('now'))
            """, (
                topic.get('title', ''),
                topic.get('description', ''),
                topic.get('learning_time', '1-3 дня'),
                topic.get('difficulty', 'Средний'),
                topic.get('priority', 10)
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ Сгенерировано и сохранено {len(topics)} тем по 1C на русском языке")
        
        # Покажем первые 3 темы 1C
        conn = sqlite3.connect('local_test.db')
        cursor = conn.cursor()
        cursor.execute("SELECT title, description FROM topics WHERE category = '1c' LIMIT 3")
        new_topics = cursor.fetchall()
        conn.close()
        
        print("\nПервые 3 новые темы по 1C:")
        for i, (title, desc) in enumerate(new_topics, 1):
            print(f"{i}. {title}")
            print(f"   {desc[:100]}...")
            print()
    else:
        print("❌ Не удалось сгенерировать темы по 1C")

if __name__ == "__main__":
    asyncio.run(regenerate_1c_topics())
