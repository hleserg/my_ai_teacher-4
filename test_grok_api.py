#!/usr/bin/env python3
"""Тест подключения к Grok API"""

import asyncio
import os
import aiohttp

async def test_grok_api():
    # Устанавливаем переменную окружения
    
    api_key = os.getenv('GROK_API_KEY')
    base_url = 'https://api.x.ai/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a test assistant."
            },
            {
                "role": "user",
                "content": "Testing. Just say hi and hello world and nothing else."
            }
        ],
        "model": "grok-4-latest",
        "stream": False,
        "temperature": 0
    }
    
    print("🔄 Тестируем подключение к Grok API...")
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
    print(f"🌐 URL: {base_url}")
    print(f"📝 Model: {payload['model']}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(base_url, headers=headers, json=payload) as response:
                print(f"📊 Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    print(f"✅ Успешный ответ: {content}")
                else:
                    error_text = await response.text()
                    print(f"❌ Ошибка {response.status}: {error_text}")
                    
    except Exception as e:
        print(f"❌ Исключение: {e}")

if __name__ == '__main__':
    asyncio.run(test_grok_api())
