import os
import logging
import asyncio
import signal
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
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

    async def _send_loading_indicator(self, update_or_query, message: str = "⏳ Обрабатываю запрос, пожалуйста подождите...", context=None):
        """Отправляет индикатор загрузки"""
        try:
            if hasattr(update_or_query, 'message') and update_or_query.message:
                # Это callback query
                loading_msg = await update_or_query.message.reply_text(message)
            elif hasattr(update_or_query, 'effective_chat'):
                # Это обычный update
                loading_msg = await update_or_query.message.reply_text(message)
            else:
                return None
            return loading_msg
        except Exception as e:
            logger.error(f"Ошибка отправки индикатора загрузки: {e}")
            return None

    async def _delete_loading_message(self, loading_msg):
        """Удаляет сообщение с индикатором загрузки"""
        try:
            await loading_msg.delete()
        except Exception:
            # Игнорируем ошибки удаления (сообщение может быть уже удалено)
            pass
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start - приветствие пользователя"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Друг"
        
        # Регистрируем пользователя в базе данных
        await self.db.register_user(user_id, username)
        
        welcome_message = f"""
🤖 Привет, {username}! Добро пожаловать в AI Learning Bot!

Я помогу тебе изучать новейшие технологии искусственного интеллекта.

📚 Доступные команды:
/topics - Список актуальных тем по ИИ
/topics_1c - Темы ИИ для 1C Enterprise
/progress - Твой прогресс обучения
/done - Отметить текущую тему как завершенную
/help - Помощь

Давай начнем твое путешествие в мир ИИ! 🚀
        """
        
        await update.message.reply_text(welcome_message)

    async def show_topics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /topics - показать общие темы по ИИ"""
        await self._show_topics_list(update, context, "general")

    async def show_topics_1c(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /topics_1c - показать темы для 1C Enterprise"""
        await self._show_topics_list(update, context, "1c")

    async def _show_topics_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
        """Показать список тем определенной категории"""
        try:
            # Показываем индикатор загрузки для списка тем
            loading_msg = await self._send_loading_indicator(
                update, 
                "📚 Загружаю актуальные темы...",
                context
            )
            
            topics = await self.topic_service.get_topics_by_category(category)
            
            # Удаляем сообщение загрузки
            await self._delete_loading_message(loading_msg)
            
            if not topics:
                await update.message.reply_text(
                    "🔄 Темы обновляются... Попробуйте через несколько минут."
                )
                return
            
            keyboard = []
            for i, topic in enumerate(topics[:20], 1):
                keyboard.append([
                    InlineKeyboardButton(
                        f"{i}. {topic['title'][:50]}...",
                        callback_data=f"topic_{topic['id']}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            header = "🧠 Актуальные темы по ИИ:" if category == "general" else "🏢 Темы ИИ для 1C Enterprise:"
            
            await update.message.reply_text(
                f"{header}\n\nВыберите тему для изучения:",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing topics: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при загрузке тем. Попробуйте позже."
            )

    async def handle_topic_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора темы"""
        query = update.callback_query
        await query.answer()
        
        topic_id = int(query.data.split('_')[1])
        user_id = query.from_user.id
        
        try:
            # Показываем индикатор загрузки
            loading_msg = await self._send_loading_indicator(
                query, 
                "🔄 Загружаю материалы по теме... Это может занять несколько секунд.",
                context
            )
            
            # Получаем детали темы
            topic = await self.topic_service.get_topic_by_id(topic_id)
            if not topic:
                await self._delete_loading_message(loading_msg)
                await query.edit_message_text("❌ Тема не найдена.")
                return
            
            # Устанавливаем текущую тему для пользователя
            await self.db.set_current_topic(user_id, topic_id)
            
            # Показываем прогресс
            if loading_msg:
                await loading_msg.edit_text("🤖 Генерирую персональные учебные материалы с помощью ИИ...")
            
            # Генерируем материалы для обучения (длительная операция)
            materials = await self.topic_service.generate_learning_materials(topic)
            
            # Удаляем сообщение загрузки
            await self._delete_loading_message(loading_msg)
            
            # Форматируем ответ
            response = self._format_topic_materials(topic, materials)
            
            # Кнопки для взаимодействия
            keyboard = [
                [InlineKeyboardButton("✅ Изучил!", callback_data=f"complete_{topic_id}")],
                [InlineKeyboardButton("❓ Задать вопрос", callback_data=f"question_{topic_id}")],
                [InlineKeyboardButton("📚 Назад к темам", callback_data="back_to_topics")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                response,
                reply_markup=reply_markup,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error handling topic selection: {e}")
            await query.edit_message_text("❌ Произошла ошибка. Попробуйте позже.")

    def _format_topic_materials(self, topic: Dict, materials: Dict) -> str:
        """Форматирование материалов темы"""
        response = f"""
<b>📖 {topic['title']}</b>

<i>{topic['description']}</i>

⏱️ <b>Время изучения:</b> {topic['learning_time']}
📊 <b>Сложность:</b> {topic['difficulty']}

<b>📚 Материалы для изучения:</b>

{materials.get('tutorial', '')}

<b>🔗 Полезные ссылки:</b>
{materials.get('links', '')}

<b>🎥 Видео и курсы:</b>
{materials.get('courses', '')}

<b>💡 Практические примеры:</b>
{materials.get('examples', '')}
        """
        
        return response[:4096]  # Ограничение Telegram

    async def complete_topic(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отметить тему как завершенную"""
        query = update.callback_query
        await query.answer()
        
        topic_id = int(query.data.split('_')[1])
        user_id = query.from_user.id
        
        try:
            # Отмечаем тему как завершенную
            points_earned = await self.db.complete_topic(user_id, topic_id)
            
            # Получаем статистику пользователя
            user_stats = await self.db.get_user_stats(user_id)
            
            # Сообщение о завершении
            completion_message = f"""
🎉 <b>Поздравляем!</b> Тема завершена!

✨ <b>Получено очков:</b> +{points_earned}
📊 <b>Всего очков:</b> {user_stats['total_points']}
📚 <b>Завершено тем:</b> {user_stats['completed_topics']}/20

{self._get_motivation_message(user_stats['completed_topics'])}
            """
            
            # Кнопка возврата к темам
            keyboard = [[InlineKeyboardButton("📚 К списку тем", callback_data="back_to_topics")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                completion_message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error completing topic: {e}")
            await query.edit_message_text("❌ Ошибка при завершении темы.")

    def _get_motivation_message(self, completed_count: int) -> str:
        """Мотивационные сообщения в зависимости от прогресса"""
        if completed_count == 1:
            return "🌟 Отличное начало! Продолжай в том же духе!"
        elif completed_count == 5:
            return "🔥 Ты на верном пути! Уже четверть пройдена!"
        elif completed_count == 10:
            return "⚡ Половина пути пройдена! Ты великолепен!"
        elif completed_count == 15:
            return "🚀 Почти финиш! Осталось совсем немного!"
        elif completed_count == 20:
            return "🏆 ПОЗДРАВЛЯЕМ! Ты изучил все темы! Ты настоящий эксперт по ИИ!"
        else:
            return "💪 Продолжай изучать! Каждый шаг приближает к цели!"

    async def show_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /progress - показать прогресс пользователя"""
        user_id = update.effective_user.id
        
        try:
            # Показываем индикатор загрузки для статистики
            loading_msg = await self._send_loading_indicator(
                update, 
                "📊 Собираю вашу статистику обучения...",
                context
            )
            
            stats = await self.db.get_user_stats(user_id)
            completed_topics = await self.db.get_completed_topics(user_id)
            
            # Удаляем сообщение загрузки
            await self._delete_loading_message(loading_msg)
            
            progress_bar = self._create_progress_bar(stats['completed_topics'], 20)
            
            progress_message = f"""
📊 <b>Ваш прогресс обучения</b>

{progress_bar} {stats['completed_topics']}/20

✨ <b>Очки:</b> {stats['total_points']}
📅 <b>Дней изучения:</b> {stats['learning_days']}
🔥 <b>Текущий стрик:</b> {stats['streak']} дней

<b>🎓 Завершенные темы:</b>
            """
            
            for topic in completed_topics:
                progress_message += f"✅ {topic['title']}\n"
            
            await update.message.reply_text(
                progress_message,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error showing progress: {e}")
            await update.message.reply_text("❌ Ошибка при загрузке прогресса.")

    def _create_progress_bar(self, completed: int, total: int) -> str:
        """Создание визуальной полосы прогресса"""
        filled = int((completed / total) * 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"[{bar}]"

    async def handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка вопросов пользователя о текущей теме"""
        user_id = update.effective_user.id
        question = update.message.text
        
        try:
            # Получаем текущую тему пользователя
            current_topic = await self.db.get_current_topic(user_id)
            
            if not current_topic:
                await update.message.reply_text(
                    "❓ Сначала выберите тему для изучения командой /topics"
                )
                return
            
            # Показываем индикатор загрузки
            loading_msg = await self._send_loading_indicator(
                update, 
                "🤔 Анализирую ваш вопрос и готовлю подробный ответ...",
                context
            )
            
            # Генерируем ответ через Grok API (длительная операция)
            answer = await self.grok_service.answer_question(question, current_topic)
            
            # Удаляем сообщение загрузки
            await self._delete_loading_message(loading_msg)
            
            await update.message.reply_text(
                f"💡 <b>Ответ по теме \"{current_topic['title']}\":</b>\n\n{answer}",
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error handling question: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке вопроса. Попробуйте позже."
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help - справка"""
        help_text = """
🤖 <b>AI Learning Bot - Справка</b>

<b>📚 Основные команды:</b>
/start - Начать работу с ботом
/topics - Список актуальных тем по ИИ
/topics_1c - Темы ИИ для 1C Enterprise
/progress - Ваш прогресс обучения
/done - Завершить текущую тему
/help - Эта справка

<b>❓ Как пользоваться:</b>
1. Выберите тему из списка
2. Изучите материалы
3. Задавайте вопросы по теме
4. Отметьте тему как завершенную
5. Получайте очки и достижения!

<b>🎮 Система очков:</b>
• Завершение темы: 100 очков
• Ежедневное изучение: +10 очков к стрику

<b>❓ Вопросы и поддержка:</b>
Просто напишите свой вопрос после выбора темы, и я отвечу!
        """
        
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def update_topics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /update_topics - ручное обновление тем (только для админа)"""
        # Проверка на админа (замените на ваш Telegram ID)
        admin_ids = [152423085]  # Добавьте свой Telegram ID
        
        if update.effective_user.id not in admin_ids:
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        try:
            await update.message.reply_text("🚀 Запускаю обновление тем...")
            
            # Обновляем общие темы
            await update.message.reply_text("📚 Обновляю общие темы по ИИ...")
            await self.topic_service._generate_and_save_topics("general")
            
            # Обновляем темы 1C
            await update.message.reply_text("🏢 Обновляю темы ИИ для 1C Enterprise...")
            await self.topic_service._generate_and_save_topics("1c")
            
            await update.message.reply_text("✅ Все темы успешно обновлены!")
            
        except Exception as e:
            logger.error(f"Ошибка обновления тем: {e}")
            await update.message.reply_text(f"❌ Ошибка при обновлении тем: {str(e)}")

    async def back_to_topics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Возврат к списку тем"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("🧠 Общие темы ИИ", callback_data="show_general_topics")],
            [InlineKeyboardButton("🏢 Темы для 1C", callback_data="show_1c_topics")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📚 Выберите категорию тем:",
            reply_markup=reply_markup
        )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Update {update} caused error {context.error}")

    async def scheduled_topics_update(self, context: ContextTypes.DEFAULT_TYPE):
        """Обновление тем по расписанию"""
        try:
            logger.info("📅 Запуск еженедельного обновления тем...")
            
            # Обновляем общие темы
            logger.info("📚 Обновляем общие темы по ИИ...")
            await self.topic_service._generate_and_save_topics("general")
            logger.info("✅ Общие темы обновлены")
            
            # Обновляем темы 1C
            logger.info("🏢 Обновляем темы ИИ для 1C Enterprise...")
            await self.topic_service._generate_and_save_topics("1c")
            logger.info("✅ Темы 1C обновлены")
            
            logger.info("🎉 Еженедельное обновление тем завершено!")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении тем по расписанию: {e}")

    def run(self):
        """Запуск бота с инициализацией сервисов"""
        
        async def init_and_run():
            # Инициализация сервисов
            await self.db.init_db()
            logger.info("✅ База данных инициализирована")
            
            await self.topic_service.initialize_topics()
            logger.info("✅ Темы инициализированы")
            
            logger.info("🤖 Бот готов к работе!")
            
            # Создание приложения
            application = Application.builder().token(self.token).build()
            
            # Регистрация обработчиков команд
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("topics", self.show_topics))
            application.add_handler(CommandHandler("topics_1c", self.show_topics_1c))
            application.add_handler(CommandHandler("progress", self.show_progress))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("update_topics", self.update_topics_command))
            
            # Обработчики callback запросов
            application.add_handler(CallbackQueryHandler(self.handle_topic_selection, pattern="^topic_"))
            application.add_handler(CallbackQueryHandler(self.complete_topic, pattern="^complete_"))
            application.add_handler(CallbackQueryHandler(self.back_to_topics, pattern="^back_to_topics"))
            
            # Обработчик текстовых сообщений (вопросы)
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_question))
            
            # Обработчик ошибок
            application.add_error_handler(self.error_handler)
            
            # Настройка расписания для обновления тем
            job_queue = application.job_queue
            
            # Обновление тем каждое воскресенье в 3:00 ночи
            job_queue.run_repeating(
                self.scheduled_topics_update,
                interval=timedelta(weeks=1),  # Каждую неделю
                first=datetime.now().replace(hour=3, minute=0, second=0, microsecond=0) + timedelta(days=(6 - datetime.now().weekday()) % 7),  # Следующее воскресенье в 3:00
                name="weekly_topics_update"
            )
            logger.info("⏰ Настроено еженедельное обновление тем (Воскресенье 03:00)")
            
            # Инициализация и запуск вручную
            logger.info("🤖 AI Learning Bot запущен!")
            
            await application.initialize()
            
            try:
                await application.updater.start_polling()
                await application.start()
                
                # Ждем бесконечно
                stop_signals = (signal.SIGTERM, signal.SIGINT)
                if stop_signals:
                    for sig in stop_signals:
                        signal.signal(sig, lambda s, f: None)
                
                # Блокируемся до сигнала
                while True:
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                logger.info("👋 Получен сигнал остановки")
            finally:
                await application.stop()
                await application.updater.stop()
                await application.shutdown()
        
        # Запуск в новом event loop
        try:
            asyncio.run(init_and_run())
        except KeyboardInterrupt:
            logger.info("👋 Бот остановлен")
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
            raise

if __name__ == '__main__':
    bot = AILearningBot()
    bot.run()
