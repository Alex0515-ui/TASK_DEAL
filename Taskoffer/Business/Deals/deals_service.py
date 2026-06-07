from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from Business.Deals.deal_schemas import ChangeDealSchema, CancelDealSchema
from Business.Jobs.job_models import Job
from Business.Job_responses.job_response_models import JobResponse
from Business.Deals.deal_models import Deal, DealStatus
from Core.auth.user_models import User
from Interactions.Payment.payment_models import Wallet, Transaction, TransactionType
from Interactions.Notifications.notification_models import NotificationType

from Interactions.Notifications.notification_service import create_notification
from Interactions.Payment.payment_service import process_job_payment, DealPaymentAction


class DealService:

    # Создание сделки (Автоматическое платформой)
    @staticmethod
    def createDeal(job: Job, job_response: JobResponse, db: Session):

        # Защита от Race Condition 
        job = db.execute(select(Job).where(Job.id == job.id).with_for_update()).scalar_one()

        existing = db.execute(select(Deal).where(Deal.job_id == job.id)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Сделка уже существует!')
        
        worker = db.get(User, job_response.worker_id)
        client = db.get(User, job.owner_id)

        if not worker or not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Клиент или работник не существует')
        
        deal = Deal(
            job_id = job.id,
            worker_id = worker.id,
            client_id = client.id,
            worker_email=worker.email, 
            client_email=client.email, 
            deadline=job.deadline,
            worker_phone_number=worker.phone_number, 
            client_phone_number=client.phone_number
        )

        if job_response.offered_price is not None:
            deal.agreed_price = job_response.offered_price
            job.price = job_response.offered_price

        else:
            deal.agreed_price = job.price
        
        create_notification(
            user_id=deal.client_id, 
            text=f"Создан договор по работе '{job.title}', пожалуйста ознакомьтесь", 
            db=db,
            type=NotificationType.JOB,
            related_id=job.id
        )

        create_notification(
            user_id=deal.worker_id, 
            text=f"Создан договор по работе '{job.title}', пожалуйста ознакомьтесь", 
            db=db,
            type=NotificationType.JOB,
            related_id=job.id
        )

        db.add(deal)
        db.commit()
        return deal
    

    # Получение сделки
    @staticmethod
    def find_deal(deal_id: int, user_id: int, db: Session):
        deal = db.get(Deal, deal_id)

        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if user_id not in [deal.worker_id, deal.client_id]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя посмотреть чужую сделку!')
        
        return deal


    # Изменение сделки
    @staticmethod
    def change_deal_conditions(data: ChangeDealSchema, deal_id: int, user_id: int, db: Session):
        deal = db.execute(select(Deal).where(Deal.id == deal_id).with_for_update()).scalar_one_or_none()

        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if deal.client_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Сделку может менять только его заказчик!')
        
        if deal.status == DealStatus.CANCELLED:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Нельзя изменить отмененную сделку!')
        
        if deal.status == DealStatus.COMPLETED:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Нельзя изменить завершенную сделку!')
        
        deal_changed = False

        if data.agreed_price is not None and data.agreed_price != deal.agreed_price:
            if data.agreed_price > deal.agreed_price:
                price_difference = data.agreed_price - deal.agreed_price

                client_wallet = db.execute(select(Wallet).where(Wallet.user_id == deal.client_id).with_for_update()).scalar_one_or_none()

                if not client_wallet:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Кошелек не найден')
                
                if client_wallet.balance < price_difference:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Для изменения сделки, в кошельке должна быть сумма: {price_difference}')
                
                client_wallet.balance -= price_difference

                transaction = Transaction(
                    type=TransactionType.HOLD,
                    wallet_id=client_wallet.id,
                    deal_id=deal.id,
                    amount=price_difference
                )
                db.add(transaction)

            deal.agreed_price = data.agreed_price
            deal_changed = True

        if data.deadline is not None and data.deadline != deal.deadline:
            deal.deadline = data.deadline
            deal_changed = True
        
        # Обнуляю подписи при изменении сделки, чтобы не было обмана
        if deal_changed:
            deal.change_reason = data.reason
            deal.last_action_by = user_id
            deal.worker_signed_at = None
            deal.client_signed_at = None
            deal.is_fully_signed = False
            deal.status = DealStatus.NEGOTIATION
            deal.started_at = None
        
        create_notification(
            user_id=deal.worker_id, 
            text=f"Был изменен договор по работе '{deal.job.title}'\nПожалуйста ознакомьтесь", 
            db=db,
            type=NotificationType.JOB,
            related_id=deal.job.id
        )

        db.commit()
        return {"message": "Сделка успешно обновлена! Подпишите ее с обеих сторон!"}
    

    # Подписание о начале работы
    @staticmethod
    def first_sign_deal(deal_id: int, user_id: int, db: Session):
        deal = db.execute(select(Deal).where(Deal.id == deal_id).with_for_update()).scalar_one_or_none()

        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if deal.status != DealStatus.NEGOTIATION:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Подписи уже поставлены')
        
        now = datetime.now(timezone.utc)

        if user_id not in [deal.client_id, deal.worker_id]:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Нельзя подписать чужую сделку')
        
        if user_id == deal.client_id:
            if deal.client_signed_at:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Вы уже подписали')
            
            deal.client_signed_at = now
            message = "Сделка успешно подписана! Осталось подписать работнику, для начала работы"
            create_notification(
                user_id=deal.worker_id, 
                text=f"Клиент подписал договор по работе '{deal.job.title}'\nТеперь нужна подпись с вашей стороны для начала работы",
                type=NotificationType.JOB,
                db=db,
                related_id=deal.job.id
            )
        
        elif user_id == deal.worker_id:
            if deal.worker_signed_at:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Вы уже подписали')
            
            deal.worker_signed_at = now
            message = "Сделка успешно подписана! Осталось подписать клиенту, для начала работы"
            create_notification(
                user_id=deal.client_id, 
                text=f"Работник подписал договор по работе '{deal.job.title}'\nТеперь нужна подпись с вашей стороны для начала работы",
                type=NotificationType.JOB,
                db=db,
                related_id=deal.job.id
            )
        
        if deal.client_signed_at and deal.worker_signed_at:
            deal.status = DealStatus.ACTIVE
            deal.started_at = now
            message = "Сделка успешно подписана с обеих сторон! Можете приступать к работе"
            deal.is_fully_signed = True

        db.commit()
        return {"message": message}


    # Подпись о завершении работы
    @staticmethod
    def complete_deal(deal_id: int, user_id: int, db: Session):
        deal = db.execute(select(Deal).where(Deal.id == deal_id).with_for_update()).scalar_one_or_none()
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if deal.status != DealStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Сначала нужна подпись с обеих сторон о начале работы !')

        now = datetime.now(timezone.utc)

        if user_id not in [deal.worker_id, deal.client_id]:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Нельзя подписать чужую сделку')
        
        if user_id == deal.client_id:
            if deal.client_completed_at:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Вы уже подписали о завершении')
            
            deal.client_completed_at = now
            message = "Сделка успешно подписана! Для завершения осталось подписать работнику"
            if deal.worker_completed_at is None:
                create_notification(
                    user_id=deal.worker_id, 
                    text=f"Клиент подписал договор по работе '{deal.job.title}'\nТеперь нужна подпись с вашей стороны для завершения работы",
                    type=NotificationType.JOB,
                    db=db,
                    related_id=deal.job.id
                )
        
        elif user_id == deal.worker_id:
            if deal.worker_completed_at:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Вы уже подписали о завершении')
            
            deal.worker_completed_at = now
            message = "Сделка успешно подписана! Для завершения осталось подписать клиенту"
            if deal.client_completed_at is None:
                create_notification(
                    user_id=deal.client_id, 
                    text=f"Работник подписал договор по работе '{deal.job.title}'\nТеперь нужна подпись с вашей стороны для завершения работы",
                    type=NotificationType.JOB,
                    db=db,
                    related_id=deal.job.id
                )
        
        if deal.client_completed_at and deal.worker_completed_at:
            deal.status = DealStatus.COMPLETED
            deal.completed_at = now
            message = "Сделка успешно завершена с обеих сторон!"
            process_job_payment(action=DealPaymentAction.COMPLETE_DEAL, amount=deal.agreed_price, db=db, deal_id=deal.id, client_id=deal.client_id, worker_id=deal.worker_id)

        db.commit()
        return {"message": message}
    

    # Отмена сделки
    @staticmethod
    def cancel_deal(deal_id: int, user_id: int, data: CancelDealSchema, db: Session):
        deal = db.execute(select(Deal).where(Deal.id == deal_id).with_for_update()).scalar_one_or_none()

        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if user_id not in [deal.worker_id, deal.client_id]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя отменить чужую сделку')
        
        if deal.status == DealStatus.COMPLETED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Сделка уже завершена')
        
        if deal.status == DealStatus.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Сделка уже отменена')
        
        deal.cancel_reason = data.reason
        deal.last_action_by = user_id
        deal.status = DealStatus.CANCELLED
        deal.cancelled_at = datetime.now(timezone.utc)

        other_user_id = deal.worker_id if user_id == deal.client_id else deal.client_id
        create_notification(
            user_id=other_user_id, 
            text=f"Договор по работе '{deal.job.title}' был отменен",
            type=NotificationType.JOB,
            db=db,
            related_id=deal.job.id
        )

        process_job_payment(
            action=DealPaymentAction.DEAL_CANCEL, 
            amount=deal.agreed_price, 
            db=db, 
            deal_id=deal.id, 
            client_id=deal.client_id, 
            worker_id=deal.worker_id
        )

        db.commit()

        return {"message": "Сделка отменена"}
        
        
   


