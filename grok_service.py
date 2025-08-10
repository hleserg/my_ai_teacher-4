import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GrokService:
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        self.base_url = 'https://api.x.ai/v1/chat/completions'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

    async def generate_ai_topics(self, category: str = "general") -> List[Dict]:
        """Генерация списка актуальных тем по ИИ"""
        
        if category == "1c":
            prompt = """
Создай список из 20 актуальных тем по искусственному интеллекту, 
специально применимых для программирования на 1C Enterprise на август 2025 года.

Каждая тема должна:
1. Быть релевантной для 1C Enterprise разработчиков
2. Изучаться за 1-3 дня
3. Иметь практическое применение в 1C
4. Быть основанной на реальных технологиях

Верни результат в JSON формате:
[
  {
    "title": "Название темы",
    "description": "Краткое описание (2-3 предложения)",
    "learning_time": "1-2 дня",
    "difficulty": "Начинающий/Средний/Продвинутый",
    "priority": число от 1 до 20
  }
]

Упорядочи по актуальности и применимости для 1C Enterprise.
            """
        else:
            prompt = """
Создай список из 20 самых актуальных тем по искусственному интеллекту 
для программистов на текущую дату.

Каждая тема должна:
1. Быть релевантной и полезной для программистов
2. Изучаться за 1-3 дня  
3. Иметь доступные ресурсы для обучения
4. Быть основанной на реальных, существующих технологиях

Верни результат в JSON формате:
[
  {
    "title": "Название темы",
    "description": "Краткое описание (2-3 предложения)", 
    "learning_time": "1-2 дня",
    "difficulty": "Начинающий/Средний/Продвинутый",
    "priority": число от 1 до 20
  }
]

Упорядочи по актуальности на август 2025 года.
            """

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты эксперт по искусственному интеллекту и современным технологиям. Создавай только реалистичные и практические темы на основе существующих технологий. ВСЯ ИНФОРМАЦИЯ ДОЛЖНА БЫТЬ НА РУССКОМ ЯЗЫКЕ, включая названия, описания и все тексты."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "model": "grok-4-latest",
                    "stream": False,
                    "temperature": 0.3
                }

                async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Парсим JSON из ответа
                        try:
                            # Ищем JSON в ответе
                            start = content.find('[')
                            end = content.rfind(']') + 1
                            if start != -1 and end != 0:
                                json_str = content[start:end]
                                topics = json.loads(json_str)
                                
                                # Добавляем категорию к каждой теме
                                for topic in topics:
                                    topic['category'] = category
                                
                                logger.info(f"Сгенерировано {len(topics)} тем для категории {category}")
                                return topics
                            else:
                                logger.error("JSON не найден в ответе Grok")
                                return []
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"Ошибка парсинга JSON: {e}")
                            return []
                    else:
                        logger.error(f"Ошибка API Grok: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Ошибка генерации тем: {e}")
            return []

    async def generate_learning_materials(self, topic: Dict) -> Dict:
        """Генерация материалов для изучения темы"""
        
        prompt = f"""
Создай подробные материалы для изучения темы: "{topic['title']}"

Описание темы: {topic.get('description', '')}
Время изучения: {topic.get('learning_time', '1-3 дня')}
Уровень: {topic.get('difficulty', 'Средний')}

Создай материалы в следующем формате НА РУССКОМ ЯЗЫКЕ:

TUTORIAL:
Краткое введение в тему (3-4 абзаца), объяснение основных концепций, пошаговый план изучения.

LINKS:
• Официальная документация: [название](URL)
• GitHub репозитории с примерами: [название](URL)  
• Полезные статьи: [название](URL)

COURSES:
• YouTube видео: [название канала - название видео](URL)
• Онлайн курсы: [платформа - название курса](URL)

EXAMPLES:
Практические примеры кода или упражнения для закрепления материала.

ВАЖНО: Весь текст, объяснения, комментарии к коду и описания должны быть на русском языке.
Убедись, что все ссылки ведут на реальные, существующие ресурсы. Если не уверен в URL, используй заглушки вида [найди: "ключевые слова для поиска"].
        """

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты эксперт-преподаватель по искусственному интеллекту. Создавай качественные, структурированные материалы для быстрого изучения технологий. ВСЯ ИНФОРМАЦИЯ И МАТЕРИАЛЫ ДОЛЖНЫ БЫТЬ НА РУССКОМ ЯЗЫКЕ."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "grok-4-latest", 
                    "stream": False,
                    "temperature": 0.2
                }

                async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        logger.info(f"Ответ от Grok API (первые 500 символов): {content[:500]}...")
                        logger.info(f"ПОЛНЫЙ ОТВЕТ ОТ API: {content}")  # Добавили полное логирование
                        
                        # Парсим структурированный ответ
                        materials = self._parse_materials(content)
                        logger.info(f"Спарсенные материалы: tutorial={len(materials.get('tutorial', ''))}, links={len(materials.get('links', ''))}")
                        return materials
                    else:
                        logger.error(f"Ошибка API при генерации материалов: {response.status}")
                        error_text = await response.text()
                        logger.error(f"Детали ошибки: {error_text}")
                        return self._default_materials()
                        
        except Exception as e:
            logger.error(f"Ошибка генерации материалов: {e}")
            return self._default_materials()

    async def answer_question(self, question: str, topic: Dict) -> str:
        """Ответ на вопрос пользователя по текущей теме"""
        
        prompt = f"""
Пользователь изучает тему: "{topic['title']}"
Описание темы: {topic.get('description', '')}

Вопрос пользователя: {question}

Дай точный, краткий и полезный ответ на вопрос в контексте изучаемой темы НА РУССКОМ ЯЗЫКЕ.
Ответ должен быть:
- Понятным для изучающего эту тему
- Практически применимым
- Не более 3-4 абзацев
- С примерами кода, если уместно
- Все комментарии в коде должны быть на русском языке
        """

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": [
                        {
                            "role": "system", 
                            "content": "Ты эксперт-наставник по ИИ. Отвечай четко, кратко и полезно на вопросы учеников. ВСЕ ОТВЕТЫ ДОЛЖНЫ БЫТЬ НА РУССКОМ ЯЗЫКЕ."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "grok-4-latest",
                    "stream": False,
                    "temperature": 0.1
                }

                async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        answer = data['choices'][0]['message']['content']
                        
                        # Ограничиваем длину ответа для Telegram
                        if len(answer) > 3000:
                            answer = answer[:3000] + "..."
                        
                        return answer
                    else:
                        logger.error(f"Ошибка API при ответе на вопрос: {response.status}")
                        return "❌ Извините, произошла ошибка при обработке вашего вопроса. Попробуйте позже."
                        
        except Exception as e:
            logger.error(f"Ошибка ответа на вопрос: {e}")
            return "❌ Произошла техническая ошибка. Пожалуйста, попробуйте задать вопрос позже."

    async def monitor_ai_news(self) -> List[Dict]:
        """Мониторинг новостей по ИИ технологиям"""
        
        prompt = """
Найди и обобщи 5-7 самых важных новостей в области искусственного интеллекта за последнюю неделю, 
которые будут полезны программистам для изучения.

Фокусируйся на:
- Новые фреймворки и библиотеки
- Обновления существующих инструментов
- Важные релизы и анонсы
- Новые техники и подходы

Для каждой новости укажи НА РУССКОМ ЯЗЫКЕ:
- Заголовок
- Краткое описание (2-3 предложения)
- Почему это важно для программистов
- Источник (если известен)

Верни в формате JSON массива объектов.
        """

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": f"Ты аналитик новостей в области ИИ. Сегодня {datetime.now().strftime('%d.%m.%Y')}. Предоставляй актуальную информацию из надежных источников. ВСЯ ИНФОРМАЦИЯ ДОЛЖНА БЫТЬ НА РУССКОМ ЯЗЫКЕ."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "model": "grok-4-latest",
                    "stream": False,
                    "temperature": 0.3
                }

                async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Парсим новости из ответа
                        try:
                            start = content.find('[')
                            end = content.rfind(']') + 1
                            if start != -1 and end != 0:
                                json_str = content[start:end]
                                news = json.loads(json_str)
                                logger.info(f"Получено {len(news)} новостей по ИИ")
                                return news
                            else:
                                logger.warning("Новости не найдены в ответе")
                                return []
                                
                        except json.JSONDecodeError:
                            logger.error("Ошибка парсинга новостей")
                            return []
                    else:
                        logger.error(f"Ошибка API при получении новостей: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Ошибка мониторинга новостей: {e}")
            return []

    def _parse_materials(self, content: str) -> Dict:
        """Парсинг структурированных материалов из ответа"""
        materials = {
            'tutorial': '',
            'links': '', 
            'courses': '',
            'examples': ''
        }
        
        try:
            logger.info(f"Парсинг материалов, длина контента: {len(content)}")
            
            sections = {
                '### TUTORIAL': 'tutorial',
                '### LINKS': 'links', 
                '### COURSES': 'courses',
                '### EXAMPLES': 'examples',
                'TUTORIAL:': 'tutorial',
                'LINKS:': 'links', 
                'COURSES:': 'courses',
                'EXAMPLES:': 'examples'
            }
            
            current_section = None
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Проверяем начало новой секции
                for section_marker, section_name in sections.items():
                    if line.startswith(section_marker):
                        current_section = section_name
                        logger.info(f"Найдена секция: {section_marker}")
                        break
                else:
                    # Добавляем содержимое к текущей секции
                    if current_section and line:
                        materials[current_section] += line + '\n'
            
            # Проверяем что получилось
            for key, value in materials.items():
                value = value.strip()
                if not value:
                    logger.warning(f"Секция {key} пустая, используем заглушку")
                    materials[key] = "Материалы будут добавлены позже."
                else:
                    logger.info(f"Секция {key}: {len(value)} символов")
                    materials[key] = value
                    
        except Exception as e:
            logger.error(f"Ошибка парсинга материалов: {e}")
            return self._default_materials()
            
        return materials

    def _default_materials(self) -> Dict:
        """Материалы по умолчанию при ошибке"""
        return {
            'tutorial': "Материалы для этой темы генерируются. Попробуйте выбрать тему позже.",
            'links': "• Ссылки будут добавлены после генерации материалов",
            'courses': "• Курсы и видео будут добавлены позже", 
            'examples': "Примеры кода будут предоставлены после обновления материалов."
        }
