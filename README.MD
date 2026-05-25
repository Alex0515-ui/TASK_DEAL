# 🛠️ Taskoffer

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-133-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)

A backend platform for quick physical tasks: clients post jobs, workers submit applications, the client picks an executor — a deal is created. Once the job is done, funds are transferred to the worker's wallet and both sides leave reviews.

---

## ⚙️ Stack

| | |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL 15 + SQLAlchemy + Alembic |
| Authentication | JWT (python-jose), Argon2/bcrypt |
| Real-time | WebSockets |
| Scheduler | APScheduler |
| Tests | pytest + httpx |

---

## 🗂️ Modules

```
Taskoffer/
├── auth/             # Registration, login, JWT
├── jobs/             # Jobs with two deadlines (applications / completion)
├── job_responses/    # Worker applications for jobs
├── deals/            # Deals: created when executor is chosen
├── payment/          # Wallets and transfers
├── reviews/          # Reviews after deal completion
├── websocket/        # Real-time chat within a deal
├── messages/         # WebSocket session messages
├── notifications/    # Platform system notifications
└── config/           # Database and environment settings
```

---

## 🚀 Getting Started

```bash
git clone https://github.com/Alex0515-ui/TASK_OFFER.git
cd TASK_OFFER/Taskoffer

cp .env.example .env
# Fill in your values in .env

docker-compose up --build
```

Once running:

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| pgAdmin | http://localhost:8081 |

Apply migrations:

```bash
docker-compose exec app alembic upgrade head
```

---

## 🗃️ Environment Variables

Copy `.env.example` to `.env`:

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

> ⚠️ Never commit `.env` with real credentials.

---

## 🧪 Tests

```bash
cd Taskoffer
python -m pytest
```
