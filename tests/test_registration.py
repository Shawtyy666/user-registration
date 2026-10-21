import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models import UserRegistration, UserRegistrationTask1, register_user


@pytest.fixture
def data():
    return {
        "username": "ivan_123", "email": "ivan@example.com",
        "password": "MyPassword123", "password_confirm": "MyPassword123",
        "age": 25, "full_name": "Иван", "phone": "+7-123-45-67",
    }


def test_success_and_serialization(data):
    before = datetime.now(timezone.utc)
    user = register_user(data)
    after = datetime.now(timezone.utc)
    assert isinstance(user, UserRegistration)
    assert before <= user.registration_date <= after
    assert "registration_date" not in data
    for output in (user.model_dump(), json.loads(user.model_dump_json())):
        assert "password_confirm" not in output
        assert "password" not in output
    assert user.password == data["password"]


def test_task1_separately(data):
    basic = {key: value for key, value in data.items() if key not in ("full_name", "phone")}
    assert UserRegistrationTask1(**basic).age == 25


@pytest.mark.parametrize("field,value,fragment", [
    ("username", "ab", "от 3 до 20"),
    ("username", "a" * 21, "от 3 до 20"),
    ("username", "иван", "латинские"),
    ("username", "ivan-123", "латинские"),
    ("username", "ivan\n", "латинские"),
    ("email", "invalid", "email"),
    ("password", "Aa1", "минимум 8"),
    ("password", "Password", "цифру"),
    ("password", "password1", "заглавную"),
    ("password", "PASSWORD1", "строчную"),
    ("password_confirm", "Other123", "совпадать"),
    ("age", 17, "не меньше 18"),
    ("age", 121, "не больше 120"),
    ("age", True, "целым"),
    ("age", "25", "целым"),
    ("age", 25.5, "целым"),
    ("full_name", "И", "минимум 2"),
    ("full_name", "", "минимум 2"),
    ("full_name", "иван", "заглавной"),
    ("full_name", "1ван", "заглавной"),
    ("phone", "+7-123-45-678", "формате"),
    ("phone", "+7-123-45-67\n", "формате"),
    ("phone", "7-123-45-67", "формате"),
    ("phone", "+７-１２３-４５-６７", "формате"),
])
def test_invalid_fields(data, field, value, fragment):
    result = register_user({**data, field: value})
    assert isinstance(result, list)
    assert any(error["field"] == field and fragment in error["message"] for error in result)


@pytest.mark.parametrize("age", [18, 120])
@pytest.mark.parametrize("username", ["abc", "A" * 20, "user_123"])
def test_boundaries(data, age, username):
    assert isinstance(register_user({**data, "age": age, "username": username}), UserRegistration)


@pytest.mark.parametrize("field", ["username", "email", "password", "password_confirm", "age", "full_name", "phone"])
def test_required(data, field):
    data.pop(field)
    assert {"field": field, "message": "Обязательное поле"} in register_user(data)


def test_multiple_errors_and_no_password_leak(data):
    result = register_user({**data, "password": "password", "age": 17, "phone": "bad"})
    assert {error["field"] for error in result} >= {"password", "age", "phone"}
    assert all(set(error) == {"field", "message"} for error in result)
    assert "MyPassword123" not in json.dumps(result)


def test_direct_model_raises(data):
    with pytest.raises(ValidationError):
        UserRegistration(**{**data, "age": 17})


def test_unknown_field(data):
    assert {"field": "unknown", "message": "Неизвестное поле"} in register_user({**data, "unknown": 1})


def test_default_factory_called_for_each_object(data):
    field = UserRegistration.model_fields["registration_date"]
    assert callable(field.default_factory)
    first = register_user(data)
    second = register_user(data)
    assert first.registration_date is not second.registration_date


def test_full_name_unicode_and_trimming(data):
    assert register_user({**data, "full_name": "  Анна  "}).full_name == "Анна"
