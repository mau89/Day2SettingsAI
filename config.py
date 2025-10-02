"""
Конфигурация для Settings AI Agent
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class Config:
    """Конфигурация приложения"""
    
    # Токены из переменных окружения
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
    YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')
    
    # Если переменные окружения не найдены, пытаемся загрузить из локального файла
    if not all([TELEGRAM_BOT_TOKEN, YANDEX_API_KEY, YANDEX_FOLDER_ID]):
        try:
            from config_local import (
                TELEGRAM_BOT_TOKEN as LOCAL_TELEGRAM_TOKEN,
                YANDEX_API_KEY as LOCAL_YANDEX_KEY,
                YANDEX_FOLDER_ID as LOCAL_YANDEX_FOLDER
            )
            TELEGRAM_BOT_TOKEN = LOCAL_TELEGRAM_TOKEN
            YANDEX_API_KEY = LOCAL_YANDEX_KEY
            YANDEX_FOLDER_ID = LOCAL_YANDEX_FOLDER
        except ImportError:
            pass

    @classmethod
    def validate(cls):
        """Проверяет, что все необходимые переменные настроены"""
        required_vars = ['TELEGRAM_BOT_TOKEN', 'YANDEX_API_KEY', 'YANDEX_FOLDER_ID']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные: {', '.join(missing_vars)}")
        
        return True