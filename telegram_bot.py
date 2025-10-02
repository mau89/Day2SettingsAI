"""
Telegram бот для Settings AI Agent
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import Config
from yandex_gpt import YandexGPTClient
from models import AgentResponse, ResponseType

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class SettingsTelegramBot:
    """Telegram бот для помощи с настройкой систем"""

    def __init__(self):
        try:
            self.gpt_client = YandexGPTClient()
            logger.info("YandexGPT клиент инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации YandexGPT клиента: {e}")
            self.gpt_client = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_message = """
🤖 Добро пожаловать в Settings AI Agent!

Я помогу вам с настройкой систем и решением технических проблем.

Доступные команды:
/start - Начать работу
/help - Показать справку
/test - Тест соединения с YandexGPT

Просто напишите мне о вашей проблеме или вопросе по настройке!
        """

        keyboard = [
            [InlineKeyboardButton("🔧 Настройки системы", callback_data="settings")],
            [InlineKeyboardButton("🐛 Решение проблем", callback_data="troubleshooting")],
            [InlineKeyboardButton("ℹ️ Общая информация", callback_data="general")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 Справка по использованию бота

Я умею помогать с:
• Настройкой операционных систем
• Решением проблем с программным обеспечением
• Конфигурацией сетевых параметров
• Устранением неполадок
• Оптимизацией производительности

Просто опишите вашу проблему или вопрос, и я предоставлю структурированный ответ с пошаговым решением.

Примеры запросов:
• "Не работает интернет на Windows 10"
• "Как настроить SSH на Ubuntu?"
• "Компьютер медленно работает"
• "Ошибка при установке программы"
        """
        await update.message.reply_text(help_text)

    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /test"""
        await update.message.reply_text("🔄 Тестирую соединение с YandexGPT...")

        if self.gpt_client is None:
            response = AgentResponse.create_error(
                message="❌ YandexGPT клиент недоступен",
                error_details="Клиент не был инициализирован",
                suggestions=["Проверьте настройки API", "Перезапустите бота"]
            )
        else:
            response = self.gpt_client.test_connection()

        await update.message.reply_text(response.to_json())

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_message = update.message.text

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        try:
            if self.gpt_client is None:
                response = AgentResponse.create_error(
                    message="❌ YandexGPT клиент недоступен",
                    error_details="Клиент не был инициализирован",
                    suggestions=["Проверьте настройки API", "Перезапустите бота"]
                )
            else:
                response = self.gpt_client.generate_response(user_message)

            await update.message.reply_text(response.to_json())
            logger.info(f"Response type: {response.type}, Confidence: {response.confidence}")

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            response = AgentResponse.create_error(
                message="❌ Ошибка при обработке сообщения",
                error_details=str(e)[:200],
                suggestions=["Попробуйте переформулировать запрос", "Попробуйте позже"]
            )
            await update.message.reply_text(response.to_json())

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback запросов от inline кнопок"""
        query = update.callback_query
        await query.answer()

        if query.data == "settings":
            response = AgentResponse.create_info(
                message="🔧 Выберите категорию настроек или опишите вашу проблему",
                data={"categories": ["Системные настройки", "Сетевые параметры", "Безопасность", "Производительность"]},
                actions=["Просто напишите, что нужно настроить!"]
            )
            await query.edit_message_text(response.to_json())

        elif query.data == "troubleshooting":
            response = AgentResponse.create_info(
                message="🐛 Опишите проблему, с которой столкнулись",
                data={"problem_types": ["Ошибки при запуске", "Проблемы с сетью", "Медленная работа", "Неполадки с оборудованием"]},
                actions=["Чем подробнее опишете, тем точнее будет решение!"]
            )
            await query.edit_message_text(response.to_json())

        elif query.data == "general":
            response = AgentResponse.create_info(
                message="ℹ️ Задайте любой вопрос по IT или настройке систем",
                data={"question_types": ["Как что-то работает", "Рекомендации по выбору", "Объяснение терминов", "Лучшие практики"]},
                actions=["Я постараюсь дать развернутый ответ!"]
            )
            await query.edit_message_text(response.to_json())

    def run(self):
        """Запускает бота"""
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("test", self.test_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.handle_callback))

        logger.info("Starting Settings AI Telegram Bot...")
        application.run_polling()