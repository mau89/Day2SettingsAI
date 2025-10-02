"""
Клиент для работы с YandexGPT API
"""

import requests
import json
import re
import logging
from typing import Dict, Any, Optional
from config import Config
from models import AgentResponse, ResponseType

logger = logging.getLogger(__name__)


class YandexGPTClient:
    """Клиент для работы с YandexGPT API"""

    def __init__(self):
        self.api_key = Config.YANDEX_API_KEY
        self.folder_id = Config.YANDEX_FOLDER_ID
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def _get_headers(self) -> Dict[str, str]:
        """Возвращает заголовки для запроса к API"""
        return {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }

    def _create_prompt(self, user_message: str) -> str:
        """Создает промпт с инструкциями по JSON формату"""
        return f"""Ты - умный помощник, работающий на базе YandexGPT. Ты можешь отвечать на любые вопросы, но особенно хорошо разбираешься в настройке систем и решении технических проблем.

ВАЖНО: Отвечай ТОЛЬКО в JSON формате, без дополнительного текста.

Формат ответа:
{{
    "type": "success|error|info|warning",
    "message": "Основное сообщение",
    "data": {{
        "category": "категория_проблемы",
        "solution": "Краткое описание решения",
        "steps": ["шаг1", "шаг2"],
        "additional_info": "Дополнительная информация"
    }},
    "actions": ["действие1", "действие2"],
    "confidence": 0.95,
    "timestamp": "2025-10-02T23:00:00.000000",
    "suggestions": null,
    "error_details": null
}}

Примеры:

Технический вопрос:
{{
    "type": "success",
    "message": "Проблема с сетью решена",
    "data": {{
        "category": "network",
        "solution": "Решение найдено",
        "steps": ["Шаг 1", "Шаг 2"],
        "additional_info": "Дополнительная информация"
    }},
    "actions": ["Действие 1", "Действие 2"],
    "confidence": 0.98,
    "timestamp": "2025-10-02T23:00:00.000000",
    "suggestions": null,
    "error_details": null
}}

Общий вопрос:
{{
    "type": "info",
    "message": "Привет! Всё хорошо, спасибо! Как дела у тебя?",
    "data": {{
        "category": "greeting",
        "solution": "Я готов помочь с любыми вопросами",
        "steps": [],
        "additional_info": "Могу помочь с техническими проблемами или просто поболтать"
    }},
    "actions": ["Задайте вопрос", "Опишите проблему"],
    "confidence": 1.0,
    "timestamp": "2025-10-02T23:00:00.000000",
    "suggestions": null,
    "error_details": null
}}

ЗАПРОС: {user_message}

ОТВЕТ:"""

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Извлекает JSON из текста"""
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'\{.*\}',
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    cleaned_match = match.strip()
                    return json.loads(cleaned_match)
                except json.JSONDecodeError:
                    continue
        return None

    def generate_response(self, user_message: str) -> AgentResponse:
        """Генерирует ответ от YandexGPT"""
        try:
            prompt = self._create_prompt(user_message)

            payload = {
                "modelUri": f"gpt://{self.folder_id}/yandexgpt",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.3,
                    "maxTokens": 2000
                },
                "messages": [
                    {
                        "role": "user",
                        "text": prompt
                    }
                ]
            }

            response = requests.post(
                self.base_url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                return AgentResponse.create_error(
                    message="❌ Ошибка API YandexGPT",
                    error_details=f"HTTP {response.status_code}: {response.text[:200]}",
                    suggestions=["Проверьте подключение к интернету", "Попробуйте позже"]
                )

            result = response.json()
            ai_response = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")

            # Парсим JSON ответ от AI
            try:
                parsed_data = json.loads(ai_response.strip())
                return AgentResponse(**parsed_data)
            except json.JSONDecodeError:
                extracted_json = self._extract_json_from_text(ai_response)
                if extracted_json:
                    try:
                        return AgentResponse(**extracted_json)
                    except Exception as e:
                        return AgentResponse.create_info(
                            message="Запрос не содержит информации для решения проблемы",
                            data={
                                "category": "unknown",
                                "solution": "Необходимо предоставить более детальное описание проблемы",
                                "steps": [
                                    "Предоставьте подробное описание проблемы",
                                    "Укажите симптомы и контекст"
                                ],
                                "additional_info": "Для корректной помощи требуется более конкретная информация о системе и возникшей проблеме"
                            },
                            actions=["Уточните запрос", "Опишите проблему подробно"],
                            confidence=0.95
                        )
                else:
                    return AgentResponse.create_info(
                        message="Запрос не содержит информации для решения проблемы",
                        data={
                            "category": "unknown",
                            "solution": "Необходимо предоставить более детальное описание проблемы",
                            "steps": [
                                "Предоставьте подробное описание проблемы",
                                "Укажите симптомы и контекст"
                            ],
                            "additional_info": "Для корректной помощи требуется более конкретная информация о системе и возникшей проблеме"
                        },
                        actions=["Уточните запрос", "Опишите проблему подробно"],
                        confidence=0.95
                    )

        except requests.exceptions.Timeout:
            return AgentResponse.create_error(
                message="⏰ Превышено время ожидания ответа от YandexGPT",
                error_details="Timeout при запросе к API",
                suggestions=["Попробуйте еще раз", "Проверьте подключение к интернету"]
            )

        except requests.exceptions.ConnectionError as e:
            return AgentResponse.create_error(
                message="❌ Ошибка соединения с YandexGPT",
                error_details=str(e)[:200],
                suggestions=["Проверьте подключение к интернету", "Попробуйте позже"]
            )

        except Exception as e:
            return AgentResponse.create_error(
                message="❌ Неожиданная ошибка при работе с YandexGPT",
                error_details=str(e)[:200],
                suggestions=["Попробуйте перезапустить бота", "Обратитесь к администратору"]
            )

    def test_connection(self) -> AgentResponse:
        """Тестирует соединение с YandexGPT API"""
        try:
            test_response = self.generate_response("Привет! Это тест соединения.")
            if test_response.type == ResponseType.ERROR:
                return test_response
            else:
                return AgentResponse.create_success(
                    message="✅ Соединение с YandexGPT работает!",
                    confidence=1.0
                )
        except Exception as e:
            return AgentResponse.create_error(
                message="❌ Ошибка при тестировании соединения с YandexGPT",
                error_details=str(e)[:200],
                suggestions=["Проверьте настройки API", "Проверьте подключение к интернету"]
            )