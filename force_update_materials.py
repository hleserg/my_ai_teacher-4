#!/usr/bin/env python3
"""Принудительное обновление материалов для конкретной темы"""

import asyncio
import os
from database import Database, LearningMaterial
from grok_service import GrokService
from topic_service import TopicService

async def force_update_materials():
    os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///local_test.db'
    
    db = Database()
    await db.init_db()
    
    grok_service = GrokService()
    topic_service = TopicService(db, grok_service)
    
    print('🔄 Принудительно обновляем материалы для темы про детекцию аномалий...')
    
    topic_dict = None
    topic_id = None
    
    # Найдем тему и получим данные
    async with db.async_session() as session:
        from sqlalchemy import select, delete
        from database import Topic
        
        result = await session.execute(
            select(Topic).where(Topic.title.like('%етекция аномалий%'))
        )
        topic = result.scalar_one_or_none()
        
        if topic:
            topic_id = topic.id  # Сохраняем id до закрытия сессии
            topic_dict = {
                'id': topic.id,
                'title': topic.title,
                'description': topic.description,
                'category': topic.category
            }
            
            print(f'📖 Обрабатываем тему: {topic.title}')
            
            # Удаляем старые материалы
            print('🗑️ Удаляем старые материалы...')
            await session.execute(
                delete(LearningMaterial).where(LearningMaterial.topic_id == topic_id)
            )
            await session.commit()
            
    # Генерируем новые материалы вне сессии
    if topic_dict and topic_id:
        # Принудительно генерируем новые материалы через Grok
        print('🤖 Генерируем новые материалы через Grok API...')
        materials = await grok_service.generate_learning_materials(topic_dict)
        print(f'✅ Получено от Grok: {len(str(materials))} символов')
        
        # Сохраняем в базу
        await topic_service._save_materials_to_db(topic_id, materials)
        print('💾 Материалы сохранены в базу данных')
        
        print('✅ Материалы полностью обновлены!')
    else:
        print('❌ Тема не найдена')

if __name__ == '__main__':
    asyncio.run(force_update_materials())
