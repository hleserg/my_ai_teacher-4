#!/usr/bin/env python3
"""
Утилита для очистки старых материалов с заглушками из базы данных
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('.env.local')
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database, LearningMaterial
from sqlalchemy import select

async def clean_placeholder_materials():
    """Очищает материалы с заглушками из базы данных"""
    
    db = Database()
    await db.init_db()
    
    try:
        async with db.async_session() as session:
            # Находим материалы с заглушками
            result = await session.execute(
                select(LearningMaterial).where(
                    LearningMaterial.content.like('%Материалы будут добавлены позже%')
                )
            )
            placeholder_materials = result.scalars().all()
            
            print(f"Найдено {len(placeholder_materials)} материалов с заглушками")
            
            # Удаляем их
            for material in placeholder_materials:
                print(f"Удаляем материал {material.material_type} для темы {material.topic_id}")
                await session.delete(material)
            
            await session.commit()
            print("✅ Очистка завершена!")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")

if __name__ == "__main__":
    asyncio.run(clean_placeholder_materials())
