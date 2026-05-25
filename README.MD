# 🛠️ Taskoffer

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-133-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)

Backend-платформа для быстрой физической работы: клиенты размещают бытовые задачи, работники подают заявки, клиент выбирает исполнителя — создаётся сделка. По завершении работы деньги поступают на кошелёк исполнителя, стороны оставляют отзывы.

---

## ⚙️ Стек

| | |
|---|---|
| Фреймворк | FastAPI |
| База данных | PostgreSQL 15 + SQLAlchemy + Alembic |
| Аутентификация | JWT (python-jose), Argon2/bcrypt |
| Real-time | WebSockets |
| Планировщик | APScheduler |
| Тесты | pytest + httpx |

---

## 🗂️ Модули

```
Taskoffer/
├── auth/             # Регистрация, логин, JWT
├── jobs/             # Задачи с двумя сроками (заявки / выполнение)
├── job_responses/    # Заявки работников на задачи
├── deals/            # Сделки: создаются при выборе исполнителя
├── payment/          # Кошельки и переводы
├── reviews/          # Отзывы после завершения сделки
├── websocket/        # Real-time чат в рамках сделки
├── messages/         # Сообщения WebSocket-сессии
├── notifications/    # Системные уведомления платформы
└── config/           # Настройки БД и окружения
```

---

## 🚀 Запуск

```bash
git clone https://github.com/Alex0515-ui/TASK_OFFER.git
cd TASK_OFFER/Taskoffer

cp .env.example .env
# Заполните .env своими значениями

docker-compose up --build
```

После запуска:

| Сервис | Адрес |
|--------|-------|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| pgAdmin | http://localhost:8081 |

Применить миграции:

```bash
docker-compose exec app alembic upgrade head
```

---

## 🗃️ Переменные окружения

Скопируйте `.env.example` в `.env`:

```env
DB_URL=postgresql://postgres:your_password@db:5432/TaskOffer
POSTGRES_DB=TaskOffer
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

JWT_SECRET_KEY=your_secret_key   # openssl rand -hex 32
ALGORITHM=HS256

PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
```

> ⚠️ Не коммитьте `.env` с реальными данными.

---

## 🧪 Тесты

```bash
cd Taskoffer
python -m pytest
```
