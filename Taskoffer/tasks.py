from apscheduler.schedulers.background import BackgroundScheduler

from datetime import datetime
from sqlalchemy import update, func
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from Core.config.database import SessionLocal
from Business.Jobs.job_models import Job, Job_status
from Business.Job_responses.job_response_models import JobResponse

scheduler = BackgroundScheduler()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Авто закрытие работ если время размещения прошло
def close_expired_jobs():
    
    with SessionLocal() as db:
        now = datetime.now()
        jobs_close = (
                update(Job)
                .where(
                    Job.status == Job_status.IN_SEARCH,
                    Job.expires_at < now
                )
                .values(status=Job_status.EXPIRED)
            ) 
        
        result = db.execute(jobs_close)
        db.commit()
        logger.info(f"Задачи просроченные закрыты: {result.rowcount}")


scheduler.add_job(close_expired_jobs, 'interval', minutes=1)


# Проверка дневного лимита создания задач
def check_daily_limit_jobs(user_id: int, db: Session):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) # Округляем до сегодняшнего 00:00

    jobs = db.query(
        func.count(Job.id)
    ).filter(
        Job.owner_id == user_id, 
        Job.created_at >= today
    ).scalar()

    return jobs >= 5
    

# Проверка дневного лимита откликов
def check_daily_limit_responses(user_id: int, db: Session):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    responses = db.query(
        func.count(JobResponse.id)
    ).filter(
        JobResponse.worker_id == user_id, 
        JobResponse.created_at >= today
    ).scalar()

    return responses >= 10



