"""Модели регистрации для заданий 1 и 2 (Pydantic 2)."""

import re
from datetime import datetime, timezone

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
)


class UserRegistrationTask1(BaseModel):
    """Исходные требования задания 1."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    username: str
    email: EmailStr
    password: str = Field(exclude=True, repr=False)
    password_confirm: str = Field(exclude=True, repr=False)
    age: int = Field(strict=True, ge=18, le=120)
    registration_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not 3 <= len(value) <= 20:
            raise ValueError("Имя пользователя должно содержать от 3 до 20 символов")
        if not re.fullmatch(r"[A-Za-z0-9_]+", value):
            raise ValueError(
                "Имя пользователя может содержать только латинские буквы, цифры и _"
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not any(char.isdigit() for char in value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not any(char.isupper() for char in value):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not any(char.islower() for char in value):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        return value

    @field_validator("password_confirm")
    @classmethod
    def validate_password_confirm(cls, value: str, info: ValidationInfo) -> str:
        # password объявлен выше: здесь доступны результаты его валидации.
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли должны совпадать")
        return value


class UserRegistration(UserRegistrationTask1):
    """Итоговая модель: все проверки задания 1 плюс поля задания 2."""

    full_name: str
    phone: str

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Реальное имя должно содержать минимум 2 символа")
        if not value[0].isupper():
            raise ValueError("Реальное имя должно начинаться с заглавной буквы")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not re.fullmatch(r"\+[0-9]-[0-9]{3}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError("Телефон должен быть в формате +X-XXX-XX-XX")
        return value


def format_errors(exc: ValidationError) -> list[dict[str, str]]:
    """Возвращает понятные ошибки без исходных данных и паролей."""
    messages = {
        "missing": "Обязательное поле",
        "string_type": "Значение должно быть строкой",
        "int_type": "Возраст должен быть целым числом",
        "greater_than_equal": "Возраст должен быть не меньше 18 лет",
        "less_than_equal": "Возраст должен быть не больше 120 лет",
        "extra_forbidden": "Неизвестное поле",
        "model_type": "Данные регистрации должны быть словарём",
    }
    errors = []
    for error in exc.errors(include_input=False, include_context=False, include_url=False):
        field = ".".join(str(part) for part in error["loc"]) or "data"
        if error["loc"] and error["loc"][0] == "email" and error["type"] != "missing":
            message = "Укажите корректный email-адрес"
        elif error["loc"] and error["loc"][0] == "registration_date":
            message = "Укажите корректные дату и время регистрации"
        else:
            message = messages.get(error["type"], error["msg"].removeprefix("Value error, "))
        errors.append({"field": field, "message": message})
    return errors


def register_user(data: dict) -> UserRegistration | list[dict[str, str]]:
    """Валидирует расширенную модель и возвращает модель либо список ошибок."""
    try:
        return UserRegistration.model_validate(data)
    except ValidationError as exc:
        return format_errors(exc)
