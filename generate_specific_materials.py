#!/usr/bin/env python3
"""Генерация материалов для конкретной темы"""

import asyncio
import os
from database import Database
from grok_service import GrokService
from topic_service import TopicService

async def generate_materials():
    os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///local_test.db'
    
    db = Database()
    await db.init_db()
    
    grok_service = GrokService()
    topic_service = TopicService(db, grok_service)
    
    print('🔄 Генерируем материалы для темы про детекцию аномалий...')
    
    # Найдем тему
    async with db.async_session() as session:
        from sqlalchemy import select
        from database import Topic
        
        result = await session.execute(
            select(Topic).where(Topic.title.like('%етекция аномалий%'))
        )
        topic = result.scalar_one_or_none()
        
        if topic:
            print(f'📖 Обрабатываем тему: {topic.title}')
            
            # Конвертируем Topic в словарь для метода
            topic_dict = {
                'id': topic.id,
                'title': topic.title,
                'description': topic.description,
                'category': topic.category
            }
            
            materials = await topic_service.generate_learning_materials(topic_dict)
            print('✅ Материалы обновлены!')
            print(f'📚 Сгенерировано: {len(materials)} типов материалов')
        else:
            print('❌ Тема не найдена')

if __name__ == '__main__':
    asyncio.run(generate_materials())
