import pytest
from Core.config.database import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from Core.entities.models import *
from datetime import datetime, timedelta, timezone
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


# ФЕЙК БД для тестов
@pytest.fixture
def db():

    URL = "sqlite:///:memory:"

    engine = create_engine(URL, connect_args={"check_same_thread": False})

    session_local_test = sessionmaker(bind=engine, expire_on_commit=False)

    Base.metadata.create_all(bind=engine)
    
    session = session_local_test()

    yield session

    session.close()


# Клиент для тестов
@pytest.fixture
def client_user(db):

    client = User(
        name="Client",
        email="client@gmail.com",
        password_hash="123",
        phone_number="77474412518",
        role=Role.CLIENT    
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    return client

# Кошелек клиента
@pytest.fixture
def client_wallet(db, client_user):
    wallet = Wallet(
        user_id=client_user.id,
        balance=20000
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)

    return wallet


# Работник для тестов
@pytest.fixture
def worker_user(db):

    worker = User(
        name="Worker",
        email="worker@gmail.com",
        password_hash="123",
        phone_number="77075130526",
        role=Role.WORKER
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    return worker

# Кошелек работника
@pytest.fixture
def worker_wallet(db, worker_user):
    wallet = Wallet(
        user_id = worker_user.id,
        balance = 0
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)

    return wallet

# Работа для теста
@pytest.fixture
def job(db, client_user, worker_user):

    after_2_days = datetime.now(timezone.utc) + timedelta(days=2)
    after_week = datetime.now(timezone.utc) + timedelta(days=7)

    job = Job(
        title="test", 
        description = "test_desc", 
        price=15000, 
        owner_id=client_user.id, 
        worker_id=worker_user.id,
        status=Job_status.ACCEPTED, 
        type=Job_type.CLEANING, 

        expires_at=after_2_days, 
        deadline = after_week
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


# Сделка для тестов обсуждение статус
@pytest.fixture
def deal_negotiation(db, client_user, worker_user, job):
    deal = Deal(
        job_id=job.id,
        worker_id=worker_user.id,
        client_id=client_user.id,
        worker_email=worker_user.email,
        client_email=client_user.email,
        worker_phone_number=worker_user.phone_number,
        client_phone_number=client_user.phone_number,
        agreed_price=job.price,
        deadline=job.deadline,
        status=DealStatus.NEGOTIATION
    )

    db.add(deal)
    db.commit()
    db.refresh(deal)

    return deal


# Сделка для тестов
@pytest.fixture
def deal(db, client_user, worker_user, job):
    deal = Deal(
        job_id=job.id,
        worker_id=worker_user.id,
        client_id=client_user.id,
        worker_email=worker_user.email,
        client_email=client_user.email,
        worker_phone_number=worker_user.phone_number,
        client_phone_number=client_user.phone_number,
        agreed_price=job.price,
        deadline=job.deadline,
        status=DealStatus.ACTIVE
    )

    db.add(deal)
    db.commit()
    db.refresh(deal)

    return deal

# Работа для тестов заявок
@pytest.fixture
def job_for_response(db, client_user, worker_user):

    after_2_days = datetime.now(timezone.utc) + timedelta(days=2)
    after_week = datetime.now(timezone.utc) + timedelta(days=7)

    job = Job(
        title="test", 
        description = "test_desc", 
        price=15000, 
        owner_id=client_user.id, 
        status=Job_status.IN_SEARCH, 
        type=Job_type.CLEANING, 

        expires_at=after_2_days, 
        deadline = after_week
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job

# Заявка для тестов
@pytest.fixture
def response(db, job_for_response, worker_user):
    response_one = JobResponse(job_id=job_for_response.id, worker_id=worker_user.id, status=Response_status.PENDING)

    db.add(response_one)
    db.commit()
    db.refresh(response_one)

    return response_one
