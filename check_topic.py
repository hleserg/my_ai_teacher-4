#!/usr/bin/env python3
"""Проверка состояния темы в базе данных"""

import asyncio
import os
from database import Database

async def check_topic():
    os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///local_test.db'
    
    db = Database()
    await db.init_db()
    
    # Найдем тему про детекцию аномалий
    async with db.async_session() as session:
        from sqlalchemy import select
        from database import Topic, LearningMaterial
        
        result = await session.execute(
            select(Topic).where(Topic.title.like('%етекция аномалий%'))
        )
        topic = result.scalar_one_or_none()
        
        if topic:
            print(f'📖 Найдена тема: {topic.title}')
            print(f'📝 Описание: {topic.description[:100]}...')
            print(f'⏰ Обновлено: {topic.updated_at}')
            
            # Проверим материалы
            materials_result = await session.execute(
                select(LearningMaterial).where(LearningMaterial.topic_id == topic.id)
            )
            materials = materials_result.scalars().all()
            
            print(f'� Материалы: {len(materials)} шт.')
            
            if materials:
                print('✅ Материалы найдены:')
                for material in materials:
                    print(f'  - {material.material_type}: {material.title}')
                    if material.content and 'генерируются' in material.content:
                        print(f'    ❌ Placeholder: {material.content[:100]}...')
                    elif material.content:
                        print(f'    ✅ Контент: {len(material.content)} символов')
            else:
                print('❌ Материалы отсутствуют')
                
        else:
            print('❌ Тема не найдена')

if __name__ == '__main__':
    asyncio.run(check_topic())
