import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from database import Database
from grok_service import GrokService
from topic_service import TopicService

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AILearningBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.db = Database()
        self.grok_service = GrokService()
        self.topic_service = TopicService(self.db, self.grok_service)
        
        # Создаем updater и dispatcher для v13
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
    def start(self, update: Update, context: CallbackContext):
        """Команда /start - приветствие пользователя"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Друг"
        
        # Регистрируем пользователя в базе данных
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
                (user_id, username)
            )
            conn.commit()
        
        welcome_text = f"Привет, {username}! 👋\n\n"
        welcome_text += "Я твой AI учитель, готовый помочь тебе изучать различные темы.\n\n"
        welcome_text += "Вот что я умею:\n"
        welcome_text += "📚 Объяснять сложные концепции простым языком\n"
        welcome_text += "🧪 Проводить тесты и квизы\n"
        welcome_text += "💡 Давать персональные рекомендации\n"
        welcome_text += "📈 Отслеживать твой прогресс\n\n"
        welcome_text += "Выбери тему для изучения:"
        
        # Создаем клавиатуру с темами
        keyboard = self._create_topics_keyboard()
        
        update.message.reply_text(welcome_text, reply_markup=keyboard)
    
    def _create_topics_keyboard(self):
        """Создает клавиатуру с доступными темами"""
        topics = self.topic_service.get_all_topics()
        
        keyboard = []
        for i in range(0, len(topics), 2):  # По 2 кнопки в ряд
            row = []
            row.append(InlineKeyboardButton(topics[i]['title'], callback_data=f"topic_{topics[i]['id']}"))
            if i + 1 < len(topics):
                row.append(InlineKeyboardButton(topics[i + 1]['title'], callback_data=f"topic_{topics[i + 1]['id']}"))
            keyboard.append(row)
        
        # Добавляем кнопку "Мой прогресс"
        keyboard.append([InlineKeyboardButton("📊 Мой прогресс", callback_data="my_progress")])
        
        return InlineKeyboardMarkup(keyboard)
    
    def help_command(self, update: Update, context: CallbackContext):
        """Команда /help - показать справку"""
        help_text = "🤖 *AI Учитель - Справка*\n\n"
        help_text += "*Основные команды:*\n"
        help_text += "/start - Начать работу с ботом\n"
        help_text += "/help - Показать эту справку\n"
        help_text += "/topics - Показать все доступные темы\n"
        help_text += "/progress - Посмотреть свой прогресс\n\n"
        help_text += "*Как пользоваться:*\n"
        help_text += "1️⃣ Выберите тему из списка\n"
        help_text += "2️⃣ Изучайте материалы\n"
        help_text += "3️⃣ Проходите тесты\n"
        help_text += "4️⃣ Отслеживайте прогресс\n\n"
        help_text += "Если возникли вопросы - просто напишите мне!"
        
        update.message.reply_text(help_text, parse_mode='Markdown')
    
    def topics_command(self, update: Update, context: CallbackContext):
        """Команда /topics - показать все темы"""
        update.message.reply_text("Выберите тему для изучения:", reply_markup=self._create_topics_keyboard())
    
    def progress_command(self, update: Update, context: CallbackContext):
        """Команда /progress - показать прогресс пользователя"""
        user_id = update.effective_user.id
        
        # Получаем прогресс пользователя
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.title, up.lessons_completed, up.total_lessons, up.progress_percentage
                FROM user_progress up
                JOIN topics t ON up.topic_id = t.id
                WHERE up.user_id = ?
                ORDER BY up.progress_percentage DESC
            """, (user_id,))
            
            progress_data = cursor.fetchall()
        
        if not progress_data:
            update.message.reply_text("У вас пока нет прогресса. Начните изучать темы!")
            return
        
        progress_text = "📊 *Ваш прогресс:*\n\n"
        for title, completed, total, percentage in progress_data:
            progress_text += f"📚 {title}\n"
            progress_text += f"   Пройдено: {completed}/{total} уроков ({percentage}%)\n"
            progress_text += f"   {'█' * int(percentage // 10)}{'░' * (10 - int(percentage // 10))} {percentage}%\n\n"
        
        update.message.reply_text(progress_text, parse_mode='Markdown')
    
    def topic_callback(self, update: Update, context: CallbackContext):
        """Обработка нажатий на кнопки тем"""
        query = update.callback_query
        query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith("topic_"):
            topic_id = int(callback_data.split("_")[1])
            self._show_topic_content(query, topic_id)
        elif callback_data == "my_progress":
            self._show_user_progress(query)
        elif callback_data.startswith("lesson_"):
            lesson_id = int(callback_data.split("_")[1])
            self._show_lesson_content(query, lesson_id)
        elif callback_data.startswith("test_"):
            topic_id = int(callback_data.split("_")[1])
            self._start_test(query, topic_id)
    
    def _show_topic_content(self, query, topic_id):
        """Показать содержание темы"""
        topic = self.topic_service.get_topic_by_id(topic_id)
        if not topic:
            query.edit_message_text("Тема не найдена.")
            return
        
        # Обновляем текущую тему пользователя
        user_id = query.from_user.id
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET current_topic_id = ? WHERE telegram_id = ?",
                (topic_id, user_id)
            )
            conn.commit()
        
        content_text = f"📚 *{topic['title']}*\n\n"
        content_text += f"{topic['description']}\n\n"
        content_text += "*Что вы изучите:*\n"
        
        # Получаем уроки для темы
        lessons = self.topic_service.get_lessons_by_topic(topic_id)
        for i, lesson in enumerate(lessons, 1):
            content_text += f"{i}. {lesson['title']}\n"
        
        # Создаем клавиатуру с уроками
        keyboard = []
        for lesson in lessons:
            keyboard.append([InlineKeyboardButton(
                f"📖 {lesson['title']}", 
                callback_data=f"lesson_{lesson['id']}"
            )])
        
        # Добавляем кнопку теста
        keyboard.append([InlineKeyboardButton("🧪 Пройти тест", callback_data=f"test_{topic_id}")])
        keyboard.append([InlineKeyboardButton("⬅️ Назад к темам", callback_data="back_to_topics")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(content_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    def _show_lesson_content(self, query, lesson_id):
        """Показать содержание урока"""
        # Здесь будет логика показа урока
        # Пока заглушка
        query.edit_message_text(
            f"📖 Урок #{lesson_id}\n\nСодержание урока будет добавлено позже...",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_topics")
            ]])
        )
    
    def _start_test(self, query, topic_id):
        """Начать тест по теме"""
        # Здесь будет логика теста
        # Пока заглушка
        query.edit_message_text(
            f"🧪 Тест по теме #{topic_id}\n\nТестирование будет добавлено позже...",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_topics")
            ]])
        )
    
    def _show_user_progress(self, query):
        """Показать прогресс пользователя"""
        user_id = query.from_user.id
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.title, up.lessons_completed, up.total_lessons, up.progress_percentage
                FROM user_progress up
                JOIN topics t ON up.topic_id = t.id
                WHERE up.user_id = ?
                ORDER BY up.progress_percentage DESC
            """, (user_id,))
            
            progress_data = cursor.fetchall()
        
        if not progress_data:
            progress_text = "У вас пока нет прогресса.\nНачните изучать темы!"
        else:
            progress_text = "📊 *Ваш прогресс:*\n\n"
            for title, completed, total, percentage in progress_data:
                progress_text += f"📚 {title}: {percentage}%\n"
        
        query.edit_message_text(
            progress_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Назад к темам", callback_data="back_to_topics")
            ]])
        )
    
    def handle_message(self, update: Update, context: CallbackContext):
        """Обработка текстовых сообщений"""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        # Получаем текущую тему пользователя
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_topic_id FROM users WHERE telegram_id = ?", (user_id,))
            result = cursor.fetchone()
            current_topic_id = result[0] if result else None
        
        if current_topic_id:
            # Генерируем ответ с помощью Grok
            try:
                response = self.grok_service.generate_educational_response(user_message, current_topic_id)
                update.message.reply_text(response)
            except Exception as e:
                logger.error(f"Ошибка генерации ответа: {e}")
                update.message.reply_text("Извините, произошла ошибка при генерации ответа. Попробуйте позже.")
        else:
            # Если тема не выбрана, предлагаем выбрать
            update.message.reply_text(
                "Сначала выберите тему для изучения:",
                reply_markup=self._create_topics_keyboard()
            )
    
    def error_handler(self, update: Update, context: CallbackContext):
        """Обработчик ошибок"""
        logger.error(f"Ошибка: {context.error}")
        if update and update.message:
            update.message.reply_text("Произошла ошибка. Попробуйте позже.")
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        # Команды
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("topics", self.topics_command))
        self.dispatcher.add_handler(CommandHandler("progress", self.progress_command))
        
        # Callback queries
        self.dispatcher.add_handler(CallbackQueryHandler(self.topic_callback))
        
        # Обработка текстовых сообщений
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        
        # Обработчик ошибок
        self.dispatcher.add_error_handler(self.error_handler)
    
    def run(self):
        """Запуск бота (синхронный метод для v13)"""
        print("🤖 Запуск бота...")
        self.setup_handlers()
        
        # Запускаем polling
        self.updater.start_polling()
        print("✅ Бот запущен и работает!")
        
        # Ожидаем остановки
        self.updater.idle()
        print("🛑 Бот остановлен.")
