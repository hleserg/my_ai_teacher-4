import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    total_points = Column(Integer, default=0)
    current_topic_id = Column(Integer, ForeignKey('topics.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_activity = Column(DateTime, default=datetime.now)
    streak = Column(Integer, default=0)
    
    # Отношения
    completed_topics = relationship("CompletedTopic", back_populates="user")
    current_topic = relationship("Topic", foreign_keys=[current_topic_id])

class Topic(Base):
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # 'general' или '1c'
    learning_time = Column(String(50))
    difficulty = Column(String(20))
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class CompletedTopic(Base):
    __tablename__ = 'completed_topics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    topic_id = Column(Integer, ForeignKey('topics.id'))
    completed_at = Column(DateTime, default=datetime.utcnow)
    points_earned = Column(Integer, default=100)
    
    # Отношения
    user = relationship("User", back_populates="completed_topics")
    topic = relationship("Topic")

class LearningMaterial(Base):
    __tablename__ = 'learning_materials'
    
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    material_type = Column(String(50))  # 'tutorial', 'link', 'video', 'example'
    title = Column(String(200))
    content = Column(Text)
    url = Column(String(500))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    topic = relationship("Topic")

class Database:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'postgresql://ai_bot:password@db:5432/ai_learning')
        self.engine = create_async_engine(self.database_url)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession)
        
    async def init_db(self):
        """Инициализация базы данных"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("База данных инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            raise

    async def register_user(self, telegram_id: int, username: str) -> bool:
        """Регистрация пользователя или обновление информации о существующем"""
        try:
            async with self.async_session() as session:
                # Ищем существующего пользователя по telegram_id
                stmt = select(User).where(User.telegram_id == telegram_id)
                result = await session.execute(stmt)
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    # Обновляем информацию о существующем пользователе
                    existing_user.username = username
                    existing_user.last_activity = datetime.now()
                    await session.commit()
                    logger.info(f"Обновлен пользователь {username} ({telegram_id})")
                    return True
                
                # Создаем нового пользователя
                user = User(
                    telegram_id=telegram_id,
                    username=username
                )
                session.add(user)
                await session.commit()
                logger.info(f"Зарегистрирован пользователь {username} ({telegram_id})")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка регистрации пользователя: {e}")
            return False

    async def set_current_topic(self, user_id: int, topic_id: int):
        """Установить текущую тему для пользователя"""
        try:
            async with self.async_session() as session:
                user = await self._get_user_by_telegram_id(session, user_id)
                if user:
                    user.current_topic_id = topic_id
                    user.last_activity = datetime.now()
                    await session.commit()
                    
        except Exception as e:
            logger.error(f"Ошибка установки текущей темы: {e}")

    async def get_current_topic(self, user_id: int) -> Optional[Dict]:
        """Получить текущую тему пользователя"""
        try:
            async with self.async_session() as session:
                user = await self._get_user_by_telegram_id(session, user_id)
                if user and user.current_topic:
                    topic = user.current_topic
                    return {
                        'id': topic.id,
                        'title': topic.title,
                        'description': topic.description,
                        'category': topic.category
                    }
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения текущей темы: {e}")
            return None

    async def complete_topic(self, user_id: int, topic_id: int) -> int:
        """Отметить тему как завершенную и начислить очки"""
        try:
            async with self.async_session() as session:
                user = await self._get_user_by_telegram_id(session, user_id)
                if not user:
                    return 0
                
                # Проверяем, не завершена ли уже эта тема
                existing_completion = await session.query(CompletedTopic).filter_by(
                    user_id=user.id, topic_id=topic_id
                ).first()
                
                if existing_completion:
                    return 0  # Тема уже завершена
                
                # Создаем запись о завершении
                points_earned = 100
                completion = CompletedTopic(
                    user_id=user.id,
                    topic_id=topic_id,
                    points_earned=points_earned
                )
                session.add(completion)
                
                # Обновляем очки пользователя
                user.total_points += points_earned
                user.current_topic_id = None
                user.last_activity = datetime.now()
                
                # Обновляем стрик
                await self._update_user_streak(session, user)
                
                await session.commit()
                return points_earned
                
        except Exception as e:
            logger.error(f"Ошибка завершения темы: {e}")
            return 0

    async def get_user_stats(self, user_id: int) -> Dict:
        """Получить статистику пользователя"""
        try:
            async with self.async_session() as session:
                user = await self._get_user_by_telegram_id(session, user_id)
                if not user:
                    return self._default_stats()
                
                completed_count = await session.query(CompletedTopic).filter_by(
                    user_id=user.id
                ).count()
                
                # Подсчет дней изучения
                learning_days = (datetime.now() - user.created_at).days + 1
                
                return {
                    'total_points': user.total_points,
                    'completed_topics': completed_count,
                    'learning_days': learning_days,
                    'streak': user.streak
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return self._default_stats()

    async def get_completed_topics(self, user_id: int) -> List[Dict]:
        """Получить список завершенных тем пользователя"""
        try:
            async with self.async_session() as session:
                user = await self._get_user_by_telegram_id(session, user_id)
                if not user:
                    return []
                
                completed = await session.query(CompletedTopic).join(Topic).filter(
                    CompletedTopic.user_id == user.id
                ).all()
                
                return [
                    {
                        'id': ct.topic.id,
                        'title': ct.topic.title,
                        'completed_at': ct.completed_at,
                        'points_earned': ct.points_earned
                    }
                    for ct in completed
                ]
                
        except Exception as e:
            logger.error(f"Ошибка получения завершенных тем: {e}")
            return []

    async def _get_user_by_telegram_id(self, session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def _update_user_streak(self, session: AsyncSession, user: User):
        """Обновить стрик пользователя"""
        today = datetime.utcnow().date()
        last_activity = user.last_activity.date() if user.last_activity else today
        
        if last_activity == today:
            # Активность сегодня - стрик продолжается
            pass
        elif last_activity == today - timedelta(days=1):
            # Вчера была активность - увеличиваем стрик
            user.streak += 1
        else:
            # Пропуск дней - сбрасываем стрик
            user.streak = 1

    def _default_stats(self) -> Dict:
        """Статистика по умолчанию"""
        return {
            'total_points': 0,
            'completed_topics': 0,
            'learning_days': 0,
            'streak': 0
        }
