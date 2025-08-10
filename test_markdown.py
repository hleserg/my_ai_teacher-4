#!/usr/bin/env python3
"""Тест генерации материалов в Markdown формате"""

import asyncio
import os
from grok_service import GrokService

async def test_markdown_generation():
    
    grok_service = GrokService()
    
    topic_dict = {
        'id': 38,
        'title': 'Детекция аномалий в данных 1C с ИИ',
        'description': 'Интегрируйте алгоритмы для выявления необычных транзакций в бухгалтерии 1C. Используйте isolation forest. Применение: предотвращение мошенничества.',
        'category': '1c',
        'learning_time': '1-2 дня',
        'difficulty': 'Средний'
    }
    
    print('🤖 Тестируем генерацию Markdown материалов...')
    
    try:
        materials = await grok_service.generate_learning_materials(topic_dict)
        print(f'✅ Материалы получены: {len(materials)} секций')
        
        # Проверим первые 500 символов каждой секции
        for key, value in materials.items():
            print(f'\n📂 {key.upper()}:')
            print(f'   Длина: {len(value)} символов')
            if value:
                # Показываем первые 300 символов для анализа Markdown
                preview = value[:300].replace('\n', '\\n')
                print(f'   Превью: {preview}...')
            else:
                print('   (пустое)')
                
    except Exception as e:
        print(f'❌ Ошибка: {e}')

if __name__ == '__main__':
    asyncio.run(test_markdown_generation())
