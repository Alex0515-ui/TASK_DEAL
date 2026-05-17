
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import update
from datetime import datetime, timezone

from Core.entities.models import *
from Interactions.Messages.message_schema import CreateMessage

class MessageService:

    # Создание сообщения
    @staticmethod
    def create_message(deal_id: int, sender_id: int, message: CreateMessage, db: Session):
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if deal.status not in [DealStatus.NEGOTIATION, DealStatus.ACTIVE]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя отправить сообщение по неактивной сделке')
        
        if sender_id not in [deal.client_id, deal.worker_id]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя отправлять сообщения в чужой чат')
        
        message = Message(deal_id=deal_id, sender_id=sender_id, text=message.text)

        db.add(message)
        db.commit()
        db.refresh(message)

        return message
    
        
    # Отметить сообщения как прочитанные
    @staticmethod
    def mark_as_read(deal_id: int, user_id: int, db:Session):
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if user_id not in [deal.client_id, deal.worker_id]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя читать чужой чат')
        
        now = datetime.now(timezone.utc)

        db.execute(
            update(Message)
            .where(
                Message.deal_id == deal_id, 
                Message.sender_id != user_id, 
                Message.read_at.is_(None)
            )
            .values(read_at=now)
        )
        db.commit()

        return {"message": "Сообщения помечены как прочитанные"}


    # Получение сообщений в чате
    @staticmethod
    def get_messages(deal_id: int, user_id: int, db: Session, offset: int = 0, limit: int = 10):
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Сделка не найдена')
        
        if user_id not in [deal.client_id, deal.worker_id]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя читать чужой чат')
        
        messages = db.query(Message).filter(Message.deal_id == deal_id)

        MessageService.mark_as_read(deal_id=deal_id, user_id=user_id, db=db)

        return messages.order_by(Message.created_at.asc()).offset(offset).limit(min(limit, 100)).all()