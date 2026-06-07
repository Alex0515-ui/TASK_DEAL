from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from Interactions.Payment.payment_models import *
from Interactions.Payment.payment_schema import WalletSchema
from enum import Enum

# Типы платежных операций по этапам работы
class DealPaymentAction(Enum):
    START_JOB = "Заморозка"
    COMPLETE_DEAL = "Завершение"
    DEAL_CANCEL = "Отмена сделки"
    JOB_CANCEL = "Отмена работы"


# Посмотреть свой кошелек
def check_balance(user_id: int, db: Session):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Кошелек не найден')
    
    return {"balance": wallet.balance}

# Пополнение кошелька
def fill_wallet(data: WalletSchema, user_id: int, db: Session):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).with_for_update().first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Кошелек не найден')
    
    transaction = Transaction(type=TransactionType.REFILL, wallet_id=wallet.id, amount=data.amount)
    wallet.balance += data.amount

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {"status": "success", "balance": wallet.balance}


# Снятие денег с кошелька
def withdraw_wallet(data: WalletSchema, user_id: int, db: Session):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).with_for_update().first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Кошелек не найден')
    
    if wallet.balance < data.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Недостаточно средств. На балансе всего {wallet.balance} тг')
    
    transaction = Transaction(type=TransactionType.WITHDRAW, wallet_id=wallet.id, amount=data.amount)
    wallet.balance -= data.amount

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {"status": "success", "balance": wallet.balance}

    
# Функция для локальных вызовов связанных с работой
def process_job_payment(action: DealPaymentAction, amount: int, db: Session, deal_id: int = None, client_id: int = None, worker_id: int = None):
    
    try:
        
        # При создании работы
        if action == DealPaymentAction.START_JOB:

            client_wallet = db.execute(select(Wallet).where(Wallet.user_id == client_id).with_for_update()).scalar_one_or_none()

            if client_wallet.balance < amount:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Недостаточно средств')
            
            client_wallet.balance -= amount
            transaction = Transaction(type=TransactionType.HOLD, wallet_id=client_wallet.id, amount=amount)
            db.add(transaction)
        
        # При завершении сделки
        elif action == DealPaymentAction.COMPLETE_DEAL:
            worker_wallet = db.execute(select(Wallet).where(Wallet.user_id == worker_id).with_for_update()).scalar_one_or_none()

            worker_wallet.balance += amount
            
            transaction = Transaction(type=TransactionType.PAYOUT, wallet_id=worker_wallet.id, amount=amount, deal_id=deal_id)
            db.add(transaction)

        # При отмене сделки
        elif action == DealPaymentAction.JOB_CANCEL or action == DealPaymentAction.DEAL_CANCEL:
            client_wallet = db.execute(select(Wallet).where(Wallet.user_id == client_id).with_for_update()).scalar_one_or_none()

            client_wallet.balance += amount

            transaction = Transaction(type=TransactionType.REFUND, wallet_id=client_wallet.id, amount=amount, deal_id=deal_id)
            db.add(transaction)
        
        return {"message": "ok"}
    
    except Exception as e:
        
        db.rollback()
        raise e



