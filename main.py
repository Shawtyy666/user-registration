"""Примеры успешной регистрации и ошибок: python main.py."""

import json

from models import UserRegistration, register_user


def main():
    data = {
        "username": "ivan_123",
        "email": "ivan@example.com",
        "password": "MyPassword123",
        "password_confirm": "MyPassword123",
        "age": 25,
        "full_name": "Иван",
        "phone": "+7-123-45-67",
    }

    result = register_user(data)
    if isinstance(result, UserRegistration):
        print("Успешная регистрация:")
        print(result.model_dump_json(indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    invalid_data = {**data, "password": "password", "age": 17, "phone": "12345"}
    print("\nОшибки регистрации:")
    print(json.dumps(register_user(invalid_data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
