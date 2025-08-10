#!/usr/bin/env python3
"""Тест генерации материалов с детальным логированием"""

import asyncio
import os
from grok_service import GrokService

async def test_materials_generation():
    
    grok_service = GrokService()
    
    topic_dict = {
        'id': 38,
        'title': 'Детекция аномалий в данных 1C с ИИ',
        'description': 'Интегрируйте алгоритмы для выявления необычных транзакций в бухгалтерии 1C. Используйте isolation forest. Применение: предотвращение мошенничества.',
        'category': '1c'
    }
    
    print('🤖 Тестируем генерацию материалов...')
    
    try:
        materials = await grok_service.generate_learning_materials(topic_dict)
        print(f'✅ Материалы получены: {len(materials)} секций')
        
        for key, value in materials.items():
            print(f'\n📂 {key.upper()}:')
            print(f'   Длина: {len(value)} символов')
            print(f'   Содержимое: {value[:200]}...' if value else '   (пустое)')
            
    except Exception as e:
        print(f'❌ Ошибка: {e}')

if __name__ == '__main__':
    asyncio.run(test_materials_generation())
