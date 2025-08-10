import logging
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from database import Database, Topic, LearningMaterial
from grok_service import GrokService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

logger = logging.getLogger(__name__)

class TopicService:
    def __init__(self, database: Database, grok_service: GrokService):
        self.db = database
        self.grok = grok_service
        self._last_update = {}  # Отслеживание последнего обновления тем

    async def get_topics_by_category(self, category: str) -> List[Dict]:
        """Получить темы по категории"""
        
        # Убираем автообновление для ускорения загрузки
        # await self._update_topics_if_needed(category)
        
        try:
            async with self.db.async_session() as session:
                result = await session.execute(
                    select(Topic).where(
                        Topic.category == category,
                        Topic.is_active == True
                    ).order_by(Topic.priority.desc())
                )
                topics = result.scalars().all()
                
                return [
                    {
                        'id': topic.id,
                        'title': topic.title,
                        'description': topic.description,
                        'learning_time': topic.learning_time,
                        'difficulty': topic.difficulty,
                        'category': topic.category,
                        'priority': topic.priority
                    }
                    for topic in topics
                ]
                
        except Exception as e:
            logger.error(f"Ошибка получения тем: {e}")
            return []

    async def get_topic_by_id(self, topic_id: int) -> Optional[Dict]:
        """Получить тему по ID"""
        try:
            async with self.db.async_session() as session:
                topic = await session.get(Topic, topic_id)
                if not topic:
                    return None
                
                return {
                    'id': topic.id,
                    'title': topic.title,
                    'description': topic.description,
                    'learning_time': topic.learning_time,
                    'difficulty': topic.difficulty,
                    'category': topic.category
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения темы {topic_id}: {e}")
            return None

    async def generate_learning_materials(self, topic: Dict) -> Dict:
        """Генерация материалов для изучения темы"""
        
        try:
            logger.info(f"Генерация материалов для темы: {topic['title']}")
            
            # Сначала проверяем, есть ли уже материалы в базе
            cached_materials = await self._get_cached_materials(topic['id'])
            if cached_materials:
                logger.info("Используем кешированные материалы")
                return cached_materials
            
            # Генерируем новые материалы через Grok
            logger.info("Генерируем новые материалы через Grok API")
            materials = await self.grok.generate_learning_materials(topic)
            logger.info(f"Получены материалы от Grok: {len(str(materials))} символов")
            
            # Сохраняем материалы в базе для кеширования
            await self._save_materials_to_db(topic['id'], materials)
            
            return materials
            
        except Exception as e:
            logger.error(f"Ошибка генерации материалов для темы {topic['id']}: {e}")
            return {
                'tutorial': "Произошла ошибка при загрузке материалов.",
                'links': "Попробуйте позже.",
                'courses': "Материалы обновляются.",
                'examples': "Примеры будут добавлены."
            }

    async def update_all_topics(self):
        """Обновить все темы из Grok API"""
        logger.info("Начинаем обновление всех тем...")
        
        try:
            # Обновляем общие темы
            await self._generate_and_save_topics("general")
            
            # Обновляем темы для 1C
            await self._generate_and_save_topics("1c")
            
            logger.info("Все темы успешно обновлены")
            
        except Exception as e:
            logger.error(f"Ошибка обновления тем: {e}")

    async def _update_topics_if_needed(self, category: str):
        """Обновить темы если прошло больше недели"""
        
        last_update = self._last_update.get(category)
        now = datetime.utcnow()
        
        # Обновляем если не обновлялись больше недели или вообще не обновлялись
        if not last_update or (now - last_update) > timedelta(days=7):
            logger.info(f"Обновляем темы категории {category}")
            await self._generate_and_save_topics(category)
            self._last_update[category] = now

    async def _generate_and_save_topics(self, category: str):
        """Генерация и сохранение тем в базу данных"""
        
        try:
            # Генерируем темы через Grok
            topics_data = await self.grok.generate_ai_topics(category)
            
            if not topics_data:
                logger.warning(f"Не удалось сгенерировать темы для категории {category}")
                return
            
            async with self.db.async_session() as session:
                # Деактивируем старые темы этой категории
                await session.execute(
                    update(Topic).where(Topic.category == category).values(is_active=False)
                )
                
                # Добавляем новые темы
                for topic_data in topics_data:
                    topic = Topic(
                        title=topic_data.get('title', ''),
                        description=topic_data.get('description', ''),
                        category=category,
                        learning_time=topic_data.get('learning_time', '1-3 дня'),
                        difficulty=topic_data.get('difficulty', 'Средний'),
                        priority=topic_data.get('priority', 0),
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(topic)
                
                await session.commit()
                logger.info(f"Сохранено {len(topics_data)} тем для категории {category}")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения тем для {category}: {e}")

    async def _get_cached_materials(self, topic_id: int) -> Optional[Dict]:
        """Получить кешированные материалы из базы данных"""
        
        try:
            async with self.db.async_session() as session:
                result = await session.execute(
                    select(LearningMaterial).where(LearningMaterial.topic_id == topic_id)
                )
                materials = result.scalars().all()
                
                if not materials:
                    return None
                
                # Проверяем, не старые ли материалы (больше 3 дней)
                oldest_material = min(materials, key=lambda x: x.created_at)
                if (datetime.utcnow() - oldest_material.created_at) > timedelta(days=3):
                    return None  # Материалы устарели
                
                # Группируем материалы по типу
                grouped_materials = {
                    'tutorial': '',
                    'links': '',
                    'courses': '',
                    'examples': ''
                }
                
                for material in materials:
                    material_type = material.material_type
                    if material_type in grouped_materials:
                        if material.content:
                            grouped_materials[material_type] += material.content + '\n'
                        if material.url:
                            grouped_materials[material_type] += f"• {material.title}: {material.url}\n"
                
                return grouped_materials
                
        except Exception as e:
            logger.error(f"Ошибка получения кешированных материалов: {e}")
            return None

    async def _save_materials_to_db(self, topic_id: int, materials: Dict):
        """Сохранить материалы в базу данных"""
        
        try:
            async with self.db.async_session() as session:
                # Удаляем старые материалы для этой темы
                await session.execute(
                    select(LearningMaterial).where(LearningMaterial.topic_id == topic_id)
                )
                
                # Сохраняем новые материалы
                for material_type, content in materials.items():
                    if content and content.strip():
                        material = LearningMaterial(
                            topic_id=topic_id,
                            material_type=material_type,
                            title=f"{material_type.title()} для темы {topic_id}",
                            content=content,
                            is_verified=False,  # Пока не проверены
                            created_at=datetime.utcnow()
                        )
                        session.add(material)
                
                await session.commit()
                logger.info(f"Материалы сохранены для темы {topic_id}")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения материалов: {e}")

    async def initialize_topics(self):
        """Инициализация тем при первом запуске"""
        logger.info("Инициализация тем...")
        
        try:
            # Проверяем, есть ли уже темы в базе
            async with self.db.async_session() as session:
                result = await session.execute(select(Topic).where(Topic.is_active == True))
                existing_topics = result.scalars().all()
                
                if len(existing_topics) < 10:  # Если тем мало, генерируем новые
                    await self.update_all_topics()
                else:
                    logger.info(f"Найдено {len(existing_topics)} активных тем, генерация не требуется")
                    
        except Exception as e:
            logger.error(f"Ошибка инициализации тем: {e}")

    async def search_topics(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Поиск тем по ключевым словам"""
        
        try:
            async with self.db.async_session() as session:
                # Базовый запрос
                base_query = select(Topic).where(Topic.is_active == True)
                
                # Добавляем фильтр по категории если указан
                if category:
                    base_query = base_query.where(Topic.category == category)
                
                # Поиск по заголовку и описанию
                search_filter = (Topic.title.ilike(f'%{query}%')) | (Topic.description.ilike(f'%{query}%'))
                base_query = base_query.where(search_filter)
                
                result = await session.execute(base_query.order_by(Topic.priority.desc()))
                topics = result.scalars().all()
                
                return [
                    {
                        'id': topic.id,
                        'title': topic.title,
                        'description': topic.description,
                        'learning_time': topic.learning_time,
                        'difficulty': topic.difficulty,
                        'category': topic.category
                    }
                    for topic in topics
                ]
                
        except Exception as e:
            logger.error(f"Ошибка поиска тем: {e}")
            return []
