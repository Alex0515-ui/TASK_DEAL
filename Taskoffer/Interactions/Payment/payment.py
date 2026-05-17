from fastapi import APIRouter

from Interactions.Payment.payment_service import *
from Core.auth.authentication import db_dependency, user_dependency
from Interactions.Payment.payment_schema import WalletSchema
from Core.entities.models import *

router = APIRouter(prefix="/wallet")

# Проверка баланса
@router.get("/my")
def check_wallet_balance(user: user_dependency, db: db_dependency):
    return check_balance(user_id=user['id'], db=db)

# Пополнение кошелька
@router.patch("/fill")
def refill_wallet(data: WalletSchema, user: user_dependency, db: db_dependency):
    return fill_wallet(data=data, user_id=user['id'], db=db)

# Снятие с баланса
@router.patch("/withdraw")
def withdrawal_wallet(data: WalletSchema, user: user_dependency, db: db_dependency):
    return withdraw_wallet(data=data, user_id=user['id'], db=db)
