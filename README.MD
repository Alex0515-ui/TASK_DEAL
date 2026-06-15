# 🛠️ Taskoffer — Task Marketplace Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-133-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)

A backend platform for quick physical task delegation: clients post jobs, workers submit applications, the client selects an executor — a deal is created. Once the job is completed, funds are transferred to the worker's wallet and both parties leave reviews.

---

## 📋 Table of Contents

- [About](#about)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Testing](#testing)

---

## About

Taskoffer solves a simple coordination problem: connecting people who need a task done with people who can do it — quickly and with financial accountability built in.

### Key Features

- **Job Posting** — clients create jobs with two deadlines: application window and completion deadline
- **Application System** — workers apply for jobs; clients review and pick an executor
- **Deal Lifecycle** — a deal is created upon executor selection and closes once the job is marked complete
- **Wallet & Payments** — funds are held and transferred automatically on deal completion
- **Review System** — both client and worker leave reviews after every completed deal
- **Real-Time Chat** — WebSocket-based messaging within each active deal
- **Notifications** — platform-level system notifications for key events
- **Scheduled Jobs** — APScheduler handles time-sensitive status transitions automatically

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Backend framework |
| PostgreSQL 15 + SQLAlchemy + Alembic | Database and migrations |
| JWT (python-jose) + Argon2/bcrypt | Authentication and password hashing |
| WebSockets | Real-time chat within deals |
| APScheduler | Background job scheduling |
| pytest + httpx | Testing |
| Docker & Docker Compose | Containerization |

---

## Project Structure

```
Taskoffer/
├── auth/             # Registration, login, JWT
├── jobs/             # Jobs with dual deadlines (application / completion)
├── job_responses/    # Worker applications for jobs
├── deals/            # Deal creation and lifecycle management
├── payment/          # Wallets and fund transfers
├── reviews/          # Post-deal reviews
├── websocket/        # Real-time chat within a deal
├── messages/         # WebSocket session messages
├── notifications/    # Platform system notifications
└── config/           # Database and environment settings
```

---

## Quick Start

### Requirements

- Docker and Docker Compose
- Filled `.env` file (see below)

### 1. Clone and Configure

```bash
git clone https://github.com/Alex0515-ui/TASK_OFFER.git
cd TASK_OFFER/Taskoffer
cp .env.example .env
# Fill in your values in .env
```

### 2. Build and Run

```bash
docker-compose up --build
```

### 3. Apply Migrations

```bash
docker-compose exec app alembic upgrade head
```

### Available Services

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| pgAdmin | http://localhost:8081 |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
DB_URL=postgresql://postgres:your_password@db:5432/TaskOffer
POSTGRES_DB=TaskOffer
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
JWT_SECRET_KEY=your_secret_key   # generate with: openssl rand -hex 32
ALGORITHM=HS256
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
```

> ⚠️ Never commit `.env` with real credentials. Always use `.env.example` as the template in version control.

---

## Testing

133 tests covering auth flows, deal lifecycle, payment logic, and WebSocket behavior.

Run locally:

```bash
cd Taskoffer
python -m pytest
```

Inside Docker:

```bash
docker-compose exec app python -m pytest
```

---

## Summary

This project demonstrates:

- Domain-driven module structure in a FastAPI application
- Full deal lifecycle: job → application → executor selection → completion → payment
- WebSocket integration for real-time in-deal communication
- Automated scheduling with APScheduler
- Wallet-based payment system with transfer logic
- Comprehensive test coverage (133 tests)
- Full containerization with Docker Compose + pgAdmin

> 👉 **Main focus:** production-grade task marketplace backend with financial accountability and real-time communication.

---

## License

MIT License
