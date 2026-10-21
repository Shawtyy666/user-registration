# Регистрация пользователей — Pydantic

Решение заданий 1 и 2 на Python 3.10+ и Pydantic 2. Задание 1 представлено моделью `UserRegistrationTask1`; итоговая `UserRegistration` наследует её и добавляет `full_name` и `phone`. Функция `register_user(data: dict)` работает с итоговой моделью.

## Установка и запуск

В терминале из папки проекта:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

macOS / Linux:

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Зависимость `pydantic[email]` устанавливает `email-validator`, необходимый для `EmailStr`.

## Требования

| Поле | Проверка |
|---|---|
| username | 3–20 символов, только латинские буквы, цифры и `_` |
| email | Валидный адрес через `EmailStr` |
| password | Не менее 8 символов, цифра, заглавная и строчная буквы |
| password_confirm | Совпадает с прошедшим проверку `password` |
| age | Строго целое число от 18 до 120 включительно |
| registration_date | Текущие дата и время UTC через `default_factory`, если поле не передано |
| full_name | Не менее 2 символов, первая буква заглавная; пробелы по краям удаляются |
| phone | Строго `+X-XXX-XX-XX`, где X — одна цифра от 0 до 9 |

`full_name` поддерживает кириллицу. Для телефона пример по условию: `+7-123-45-67`. Это проверка учебного формата, а не реального международного номера. Никакие ограничения на алфавит пароля условием не заданы, поэтому для его букв используются Unicode-проверки Python.

`registration_date` необязательно передавать: фабрика создаёт новое значение для каждого объекта. Если передать дату явно, Pydantic проверит её как `datetime`.

## Использование

```python
from models import UserRegistration, register_user

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
    print(result.model_dump_json(indent=2))
else:
    print(result)
```

При успехе возвращается объект модели. При ошибке — список вида:

```json
[
  {"field": "password", "message": "Пароль должен содержать хотя бы одну цифру"},
  {"field": "age", "message": "Возраст должен быть не меньше 18 лет"}
]
```

Для этого примера ошибок передайте `password="Password"` и `age=17`. Проверки независимых полей собираются в один список; внутри одного валидатора возвращается первая найденная ошибка. Если основной пароль не прошёл проверку, дополнительная проверка совпадения не выполняется.

Прямое создание `UserRegistration(**data)` при ошибке выбрасывает `ValidationError`, а `register_user` перехватывает её. Словарь пользователя не изменяется. Лишние поля запрещены. Числовые строки и логические значения не принимаются как возраст.

При `model_dump()` и `model_dump_json()` подтверждение пароля исключено через `Field(exclude=True)`. Сам пароль также исключён из вывода. Оба поля доступны внутри объекта, но скрыты в его `repr`. Функция возвращает ошибки без исходных значений паролей.

Это задача валидации: функция не сохраняет пользователей в базе данных и не создаёт аккаунты. HTTP-эндпоинт не добавлен, поскольку в условии требуется модель и функция.

## Тесты

Windows:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
```

macOS / Linux:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Проверяются корректная регистрация, граничные значения, ошибки каждого поля, сериализация, автосоздание даты и совместная работа проверок заданий 1 и 2.

## Файлы для GitHub

- `models.py` — модели, валидаторы и функция `register_user`.
- `main.py` — примеры запуска.
- `tests/test_registration.py` — тесты.
- `requirements.txt`, `requirements-dev.txt`, `pytest.ini`, `.gitignore`, `README.md`.

Создайте пустой публичный репозиторий на GitHub, затем выполните в папке проекта:

```bash
git init
git add .
git commit -m "Add user registration validation"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/user-registration.git
git push -u origin main
```

Замените `YOUR_USERNAME` своим именем. Для сдачи откройте `models.py` на GitHub и скопируйте ссылку на файл. Проверьте доступ к ней без входа в аккаунт.

Использованы [валидаторы Pydantic](https://pydantic.dev/docs/validation/latest/concepts/validators/) и [исключение полей при сериализации](https://pydantic.dev/docs/validation/2.12/concepts/fields/).
