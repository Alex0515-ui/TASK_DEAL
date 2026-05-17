from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from Core.entities.models import *
from Business.Job_responses.job_response_schema import CreateJobResponseSchema
from sqlalchemy import select
from Business.Deals.deals_service import DealService
from Interactions.Notifications.notification_service import create_notification
from tasks import check_daily_limit_responses

class JobResponseService:

    # Создание заявки
    @staticmethod
    def create_bind_response(data: CreateJobResponseSchema, db: Session, worker_id: int):
        
        limit = check_daily_limit_responses(user_id=worker_id, db=db)
        if limit:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Вы достигли ежедневного лимита откликов, максимальное количество: 10')
        
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Работа не найдена')
        
        if job.owner_id == worker_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Нельзя откликаться на свою работу!')
        
        if job.status != Job_status.IN_SEARCH:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Можно откликнуться только на свободную работу')
        
        existing_response = db.query(JobResponse).filter(JobResponse.job_id == data.job_id, JobResponse.worker_id == worker_id).first()
        if existing_response:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Вы уже оставляли заявку на эту работу')
        
        job_response = JobResponse(**data.model_dump(), worker_id=worker_id)

        create_notification(
            user_id=job.owner_id,
            text=f"Вам пришла заявка по работе '{job.title}'",
            type=NotificationType.JOB,
            db=db,
            related_id=job.id
        )

        db.add(job_response)
        db.commit()
        db.refresh(job_response)

        return job_response


    # Принятие заявки
    @staticmethod
    def accept_response(db: Session, response_id: int, client_id: int):
            
        try:
            response = db.execute(select(JobResponse).where(JobResponse.id == response_id).with_for_update()).scalar_one_or_none()
            if not response:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Заявка не найдена')
            
            job = db.execute(select(Job).where(Job.id == response.job.id).with_for_update()).scalar_one()

            if not job:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Работа не найдена')
            
            if job.owner_id != client_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя принять заявку на чужую работу')
            
            if job.worker_id is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Работник уже найден')
            
            # Если цена другая
            if response.offered_price:
                client_wallet = db.execute(select(Wallet).where(Wallet.user_id == client_id).with_for_update()).scalar_one_or_none()

                if response.offered_price > job.price:

                    price_difference = response.offered_price - job.price
                    
                    
                    if client_wallet.balance < price_difference:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Сумма разницы между ценой и работой нету в вашем кошельке')
                    
                    client_wallet.balance -= price_difference
                    transaction = Transaction(type=TransactionType.HOLD, wallet_id=client_wallet.id, amount=price_difference)
                
                    db.add(transaction)
                
                elif response.offered_price < job.price:
                    refund = job.price - response.offered_price

                    client_wallet.balance += refund

                    transaction = Transaction(type=TransactionType.REFUND, wallet_id=client_wallet.id, amount=refund)

                    db.add(transaction)


            job.worker_id = response.worker_id
            job.status = Job_status.ACCEPTED
            response.status = Response_status.ACCEPTED

        
            other_candidates = db.execute(
                select(JobResponse.worker_id)
                .where(JobResponse.job_id == job.id, JobResponse.id != response.id)).all()
            
            # Отклоняем других кандидатов
            db.query(JobResponse).filter(
                JobResponse.job_id == job.id, 
                JobResponse.id != response.id
            ).update({"status": Response_status.REJECTED})

            for (worker_id, ) in other_candidates:
                create_notification(
                    user_id=worker_id,
                    text=f"Ваша заявка по работе '{job.title}' к сожалению была отклонена",
                    type=NotificationType.JOB,
                    db=db,
                    related_id=job.id
                )
            
            create_notification(
                user_id=response.worker_id,
                text=f"Поздравляю!\nВаша заявка по работе '{job.title}' была принята",
                type=NotificationType.JOB,
                db=db,
                related_id=job.id
            )

            DealService.createDeal(job=job, job_response=response, db=db)

            db.commit()

            return {"message": "Работник назначен, теперь работа начнется!"}
        
        except:
            db.rollback()
            raise



    # Получение всех оставленных заявок
    @staticmethod
    def get_my_worker_responses(db: Session, worker_id: int, type: Job_type = None, job_status : Job_status = None, response_status: Response_status = None, offset: int = 0, limit: int = 10):
        responses = db.query(JobResponse).join(Job).filter(JobResponse.worker_id == worker_id)
        if type:
            responses = responses.filter(Job.type==type)

        if job_status:
            responses = responses.filter(Job.status==job_status)

        if response_status:
            responses = responses.filter(JobResponse.status == response_status)

        return responses.order_by(JobResponse.created_at.desc()).offset(offset).limit(limit).all()
    

    # Получение заявок от работников
    @staticmethod
    def get_my_client_responses(db: Session, client_id: int, job_id: int = None, type: Job_type = None, response_status: Response_status = None, offset: int = 0, limit: int = 10):
        responses = db.query(JobResponse).join(Job).filter(Job.owner_id == client_id)

        if type:
            responses = responses.filter(Job.type == type)

        if response_status:
            responses = responses.filter(JobResponse.status == response_status)

        if job_id:
            responses = responses.filter(Job.id == job_id)

        return responses.order_by(JobResponse.created_at.desc()).offset(offset).limit(limit).all()
    

    # Просмотр заявки работника
    @staticmethod
    def get_client_response(db: Session, response_id: int, client_id: int):
        response = db.query(JobResponse).join(Job).filter(JobResponse.id == response_id, Job.owner_id == client_id).first()
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Заявка не найдена')
        
        return response
    

    # Просмотр своей заявки
    @staticmethod
    def get_worker_response(db: Session, response_id: int, worker_id: int):
        response = db.query(JobResponse).filter(JobResponse.id == response_id, JobResponse.worker_id == worker_id).first()
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Заявка не найдена')
        
        return response
    
    
    # Отклонение заявки работника
    @staticmethod
    def reject_response(db: Session, response_id: int, client_id: int):
        response = db.query(JobResponse).filter(JobResponse.id == response_id).first()
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = 'Заявка не найдена')
        
        if response.job.owner_id != client_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Вы не можете отклонить заявку на чужую работу')
        
        job = db.query(Job).filter(Job.id == response.job.id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = 'Работа не найдена')
        
        if job.status == Job_status.DONE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Работа уже завершена')
        elif job.status == Job_status.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Работа уже отменена')
        
        response.status = Response_status.REJECTED

        create_notification(
            user_id=response.worker_id,
            text=f"Ваша заявка по работе '{job.title}' к сожалению была отклонена",
            type=NotificationType.JOB,
            db=db,
            related_id=job.id
        )

        db.commit()

        return {"message": "Заявка успешно отклонена"}
    
    # Отозвать заявку
    @staticmethod
    def delete_response(db: Session, response_id: int, worker_id: int, job_id: int):
        response = db.query(JobResponse).join(Job).filter(JobResponse.worker_id == worker_id, Job.id == job_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Работа не найдена')
        
        if job.status != Job_status.IN_SEARCH:
            raise HTTPException("Заявка уже принята")
        
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Заявка не найдена')
        
        db.delete(response)
        db.commit()

        return {"message": "Заявка успешно отозвана"}
    

    





    
