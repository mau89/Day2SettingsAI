#!/usr/bin/env python3
"""
Главный файл для запуска Settings AI Agent
"""

import sys
import logging
from config import Config
from telegram_bot import SettingsTelegramBot
from models import AgentResponse, ResponseType

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Главная функция запуска приложения"""
    print("🚀 Запуск Settings AI Agent...")

    try:
        Config.validate()
        print("✅ Конфигурация проверена")

        bot = SettingsTelegramBot()
        print("🤖 Бот инициализирован")
        print("📱 Запуск телеграм бота...")

        bot.run()

    except ValueError as e:
        error_response = AgentResponse.create_error(
            message="❌ Ошибка конфигурации",
            error_details=str(e),
            suggestions=[
                "Убедитесь, что настроены переменные окружения:",
                "- TELEGRAM_BOT_TOKEN",
                "- YANDEX_API_KEY", 
                "- YANDEX_FOLDER_ID",
                "Создайте файл .env с этими переменными"
            ]
        )
        
        print("\n" + "="*50)
        print("СТРУКТУРИРОВАННЫЙ ОТВЕТ ОБ ОШИБКЕ:")
        print("="*50)
        print(error_response.to_json())
        print("="*50)
        
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 Остановка бота...")
        sys.exit(0)

    except Exception as e:
        error_response = AgentResponse.create_error(
            message="❌ Ошибка запуска бота",
            error_details=str(e)[:200],
            suggestions=[
                "Проверьте подключение к интернету",
                "Убедитесь, что токены настроены правильно",
                "Попробуйте запустить бота позже"
            ]
        )

        print("\n" + "="*50)
        print("СТРУКТУРИРОВАННЫЙ ОТВЕТ ОБ ОШИБКЕ:")
        print("="*50)
        print(error_response.to_json())
        print("="*50)

        sys.exit(1)


if __name__ == "__main__":
    main()