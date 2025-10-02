"""
Модели данных для Settings AI Agent
Все ответы возвращаются в фиксированном JSON формате
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ResponseType(str, Enum):
    """Типы ответов от агента"""
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


class AgentResponse(BaseModel):
    """
    ЕДИНСТВЕННАЯ структура ответа для всех случаев
    Все ответы (успех, ошибки) возвращаются в этом формате
    """
    type: ResponseType = Field(description="Тип ответа")
    message: str = Field(description="Основное сообщение")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Дополнительные данные")
    actions: Optional[List[str]] = Field(default=None, description="Рекомендуемые действия")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Уверенность в ответе (0-1)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Время создания ответа")
    suggestions: Optional[List[str]] = Field(default=None, description="Предложения по решению")
    error_details: Optional[str] = Field(default=None, description="Детали ошибки (только для типа ERROR)")

    def to_json(self) -> str:
        """Возвращает JSON строку"""
        return self.model_dump_json(indent=2)

    def to_formatted_text(self) -> str:
        """Возвращает отформатированный текст для пользователя"""
        # Эмодзи для разных типов ответов
        type_emojis = {
            ResponseType.SUCCESS: "✅",
            ResponseType.ERROR: "❌",
            ResponseType.INFO: "ℹ️",
            ResponseType.WARNING: "⚠️"
        }

        emoji = type_emojis.get(self.type, "ℹ️")
        result = f"{emoji} {self.message}\n"

        # Добавляем данные, если есть
        if self.data:
            if "category" in self.data:
                result += f"\n🏷️ Категория: {self.data['category']}\n"

            if "steps" in self.data and self.data["steps"]:
                result += "\n📋 Пошаговое решение:\n"
                for i, step in enumerate(self.data["steps"], 1):
                    result += f"{i}. {step}\n"

            if "solution" in self.data:
                result += f"\n💡 Решение: {self.data['solution']}\n"

            if "additional_info" in self.data:
                result += f"\n📝 Дополнительно: {self.data['additional_info']}\n"

        # Добавляем рекомендуемые действия
        if self.actions:
            result += "\n🎯 Рекомендуемые действия:\n"
            for action in self.actions:
                result += f"• {action}\n"

        # Добавляем предложения (если есть)
        if self.suggestions:
            result += "\n💡 Предложения:\n"
            for suggestion in self.suggestions:
                result += f"• {suggestion}\n"

        # Добавляем детали ошибки (только для ошибок)
        if self.type == ResponseType.ERROR and self.error_details:
            result += f"\n🔍 Детали ошибки: {self.error_details}\n"

        # Добавляем уверенность
        if self.confidence is not None:
            confidence_emoji = "🟢" if self.confidence > 0.8 else "🟡" if self.confidence > 0.5 else "🔴"
            result += f"\n{confidence_emoji} Уверенность: {self.confidence:.0%}\n"

        # Добавляем время (timestamp)
        result += f"\n🕐 Время: {self.timestamp}\n"

        return result

    @classmethod
    def create_success(cls, message: str, data: Optional[Dict[str, Any]] = None, 
                      actions: Optional[List[str]] = None, confidence: float = 0.9) -> "AgentResponse":
        """Создает успешный ответ"""
        return cls(
            type=ResponseType.SUCCESS,
            message=message,
            data=data,
            actions=actions,
            confidence=confidence
        )

    @classmethod
    def create_error(cls, message: str, error_details: Optional[str] = None,
                    suggestions: Optional[List[str]] = None) -> "AgentResponse":
        """Создает ответ об ошибке"""
        return cls(
            type=ResponseType.ERROR,
            message=message,
            error_details=error_details,
            suggestions=suggestions,
            confidence=1.0
        )

    @classmethod
    def create_info(cls, message: str, data: Optional[Dict[str, Any]] = None,
                   actions: Optional[List[str]] = None) -> "AgentResponse":
        """Создает информационный ответ"""
        return cls(
            type=ResponseType.INFO,
            message=message,
            data=data,
            actions=actions,
            confidence=0.8
        )

    @classmethod
    def create_warning(cls, message: str, data: Optional[Dict[str, Any]] = None,
                      actions: Optional[List[str]] = None) -> "AgentResponse":
        """Создает предупреждение"""
        return cls(
            type=ResponseType.WARNING,
            message=message,
            data=data,
            actions=actions,
            confidence=0.7
        )