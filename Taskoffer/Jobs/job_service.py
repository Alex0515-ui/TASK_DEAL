from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from entities.models import *
from Jobs.job_schemas import CreateJobSchema
from Notifications.notification_service import create_notification
from Payment.payment_service import process_job_payment, DealPaymentAction


class JobService:

    # Создание работы пользователем
    @staticmethod
    def create_job(job_data: CreateJobSchema,  owner_id: int, db: Session):
        job = Job(**job_data.model_dump(), owner_id = owner_id)

        process_job_payment(
            action=DealPaymentAction.START_JOB, 
            amount=job_data.price, 
            db=db, 
            client_id=owner_id
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job
    
    # Работник ищет работы для выполнения
    @staticmethod
    def get_available_jobs(db: Session, job_type: Job_type = None, offset: int = 0, limit: int = 10):
        result = db.query(Job).filter(Job.status == Job_status.IN_SEARCH)
        if job_type:
            result = result.filter(Job.type == job_type)
        
        return result.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()
    

    # Клиент получает задачи которые создал
    @staticmethod
    def get_client_jobs(owner_id: int, db: Session, job_type: Job_type = None, status: Job_status = None, offset: int = 0, limit: int = 10):
        result = db.query(Job).filter(Job.owner_id == owner_id)

        if job_type:
            result = result.filter(Job.type == job_type)
        if status:
            result = result.filter(Job.status == status)
        
        return result.order_by(Job.created_at.asc()).offset(offset).limit(limit).all()
    

    # Работник получает свои задачи
    @staticmethod
    def get_worker_assigned_jobs(worker_id: int, db: Session, job_type: Job_type = None, status: Job_status = None, offset: int = 0, limit: int = 10):
        result = db.query(Job).filter(Job.worker_id == worker_id)

        if job_type:
            result = result.filter(Job.type == job_type)
        if status:
            result = result.filter(Job.status == status)
        
        return result.order_by(Job.created_at.asc()).offset(offset).limit(limit).all()
    

    # Получение одной работы
    @staticmethod
    def get_job(user_id: int, job_id: int, db:Session):
        user = db.query(User).filter(User.id==user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
       
        if user.role == Role.WORKER:
            job = db.query(Job).filter(Job.worker_id==user.id, Job.id==job_id).first()
            return job
        
        client_job = db.query(Job).filter(Job.owner_id==user.id, Job.id==job_id).first()
        return client_job
    
    # Отмена задачи
    @staticmethod
    def cancel_job(job_id: int, owner_id: int, db: Session):
        job = db.query(Job).filter(Job.id==job_id, Job.owner_id == owner_id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена или вы не являетесь ее владельцом')
        
        if job.worker_id is not None:
            create_notification(
                user_id=job.worker_id,
                text=f"Работа '{job.title}' была отменена со стороны клиента",
                type=NotificationType.JOB,
                db=db,
                related_id=job.id
            )
        
        job.status = Job_status.CANCELLED
        job.worker_id = None

        process_job_payment(
            action=DealPaymentAction.JOB_CANCEL, 
            amount=job.price, 
            db=db, 
            client_id=job.owner_id
        )

        db.commit()
        return job

    


