from fastapi import APIRouter

from Business.Deals.deals_service import DealService
from Core.auth.authentication import user_dependency, db_dependency
from Business.Deals.deal_schemas import ChangeDealSchema, CancelDealSchema

router = APIRouter(prefix="/deals")

# Получение сделки
@router.get("/get/{id}")
def get_deal(id: int, user: user_dependency, db: db_dependency):
    return DealService.find_deal(deal_id=id, user_id=user['id'], db=db)


# Изменение сделки
@router.put("/change/{id}")
def change_deal(id: int, data: ChangeDealSchema, user: user_dependency, db: db_dependency):
    return DealService.change_deal_conditions(data=data, deal_id=id, user_id=user['id'], db=db)


# Подпись о сделке
@router.patch("/sign/{id}")
def first_sign_job_deal(id: int, user: user_dependency, db: db_dependency):
    return DealService.first_sign_deal(deal_id=id, user_id=user['id'], db=db)


# Завершение работы со сделкой
@router.patch("/complete/{id}")
def complete_job_deal(id: int, user: user_dependency, db: db_dependency):
    return DealService.complete_deal(deal_id=id, user_id=user['id'], db=db)


# Отмена сделки о работе
@router.patch("/cancel/{id}")
def cancel_job_deal(id: int, data: CancelDealSchema, user: user_dependency, db: db_dependency):
    return DealService.cancel_deal(deal_id=id, user_id=user['id'], data=data, db=db)

