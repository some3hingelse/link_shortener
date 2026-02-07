# link_shortener
## Основная информация
Пет-проект на Python

Сервис-сократитель ссылок

Swagger располагается по адресу http://localhost:8000/docs

Создание ссылки http://localhost:8000/api/v1/shorten [POST]

Получение ссылки http://localhost:8000/{short}

## Используемые технологии:
- Python 3.12.10
- Основная БД - SQLite
- Миграции файлами .sql + кастомный DatabaseMigrator
- Кеш - Redis
- API метод + эндпоинт с редиректом - FastAPI
- Валидация - pydantic
- Тесты - pytest+unittest

## Настройка и запуск
### Запуск приложения
1) Переименуйте .env.example в .env
2) Внесите в .env изменения (при необходимости) 
3) Создайте файл database.db (или ваше DB_FILENAME)
4) Выполните в терминале:
    ```
   pip install -r requirements.txt
   python3 migrate.py upgrade
   pytest -v
   python3 main.py
    ```
