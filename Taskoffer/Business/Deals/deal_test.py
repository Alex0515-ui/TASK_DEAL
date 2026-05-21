from Business.Deals.deals_service import DealService
from Core.entities.models import *
from Business.Deals.deal_schemas import ChangeDealSchema, CancelDealSchema
from datetime import datetime, timedelta, timezone
from pytest_mock import mocker
import pytest
from fastapi import HTTPException
from Business.Deals.deal_schemas import ChangeDealSchema


# =======================================================================
# ====================== CREATE DEAL TESTS ======================================
# =======================================================================================

# Успешное создание сделки
def test_create_deal_success(db, worker_user, job, mocker):

    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    job_response = JobResponse(
        worker_id=worker_user.id,
        status=Response_status.ACCEPTED,
        offered_price=12000
    )

    deal = DealService.createDeal(job=job, job_response=job_response, db=db)


    assert deal is not None
    assert deal.worker_id == worker_user.id
    assert deal.client_id == job.owner_id
    assert deal.agreed_price == job_response.offered_price
    assert notification.call_count == 2


# Успешное создание сделки без предложенной цены в отклике
def test_create_deal_without_off_price(db, worker_user, job, mocker):

    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    job_response = JobResponse(
        worker_id=worker_user.id,
        status=Response_status.ACCEPTED,
    )

    deal = DealService.createDeal(job=job, job_response=job_response, db=db)


    assert deal is not None
    assert deal.worker_id == worker_user.id
    assert deal.client_id == job.owner_id
    assert deal.agreed_price == job.price
    assert notification.call_count == 2


# Ошибка что сделка существует
def test_create_deal_exists_fail(db, client_user, worker_user, job, mocker):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

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

    job_response = JobResponse(
        job_id=job.id,
        worker_id=worker_user.id,
        status=Response_status.ACCEPTED,
        offered_price=12000
    )
    with pytest.raises(HTTPException) as exc:
        DealService.createDeal(job=job, job_response=job_response, db=db)

    assert exc.value.status_code == 400
    notification.assert_not_called()


# Тест что пользователь не найден
def test_create_deal_user_not_exists_fail(db, worker_user, job, mocker):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    job_response = JobResponse(
        job_id=job.id,
        worker_id=99999,
        status=Response_status.ACCEPTED,
        offered_price=12000
    )

    with pytest.raises(HTTPException) as exc:
        DealService.createDeal(job=job, job_response=job_response, db=db)

    assert exc.value.status_code == 404
    notification.assert_not_called()


# ============================================================================
# ================= CHANGE DEAL CONDITIONS TESTS =======================
# ========================================================================================

# Успешное изменение сделки
def test_change_deal_success(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    after_two_weeks = datetime.now(timezone.utc) + timedelta(days=14)
    data = ChangeDealSchema(agreed_price=19000, deadline=after_two_weeks, reason="Just test")

    change_deal = DealService.change_deal_conditions(data=data, deal_id=deal.id, user_id=client_user.id, db=db)


    assert deal.agreed_price == data.agreed_price
    assert deal.deadline.replace(tzinfo=timezone.utc).timestamp() == data.deadline.timestamp()
    notification.assert_called_once()

# Ошибка при статусе завершенном
def test_change_deal_status_completed_fail(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    deal.status = DealStatus.COMPLETED
    db.commit()

    after_two_weeks = datetime.now(timezone.utc) + timedelta(days=14)
    data = ChangeDealSchema(agreed_price=19000, deadline=after_two_weeks, reason="Just test")

    with pytest.raises(HTTPException) as exc:
        DealService.change_deal_conditions(data=data, deal_id=deal.id, user_id=client_user.id, db=db)

    assert exc.value.status_code == 405
    notification.assert_not_called()

# Ошибка при статусе отмененном
def test_change_deal_status_cancelled_fail(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):

    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    deal.status = DealStatus.CANCELLED
    db.commit()

    after_two_weeks = datetime.now(timezone.utc) + timedelta(days=14)
    data = ChangeDealSchema(agreed_price=19000, deadline=after_two_weeks, reason="Just test")

    with pytest.raises(HTTPException) as exc:
        DealService.change_deal_conditions(data=data, deal_id=deal.id, user_id=client_user.id, db=db)

    assert exc.value.status_code == 405
    notification.assert_not_called()

# Ошибка при недостаточном балансе на кошельке
def test_change_deal_wallet_balance_fail(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    after_two_weeks = datetime.now(timezone.utc) + timedelta(days=14)
    data = ChangeDealSchema(agreed_price=40000, deadline=after_two_weeks, reason="Just test")

    with pytest.raises(HTTPException) as exc:
        DealService.change_deal_conditions(data=data, deal_id=deal.id, user_id=client_user.id, db=db)

    assert exc.value.status_code == 403
    notification.assert_not_called()


# ===========================================================================
# ====================== FIRST SIGN DEAL TESTS ================================
# ==============================================================================================

# Успешная подпись со стороны клиента 
def test_first_sign_client_success(db, mocker, worker_user, client_user, job, deal_negotiation, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    result = DealService.first_sign_deal(deal_id=deal_negotiation.id, user_id=client_user.id, db=db)

    assert deal_negotiation.client_signed_at is not None
    notification.assert_called_once()


# Успешная подпись со стороны клиента 
def test_first_sign_worker_success(db, mocker, worker_user, client_user, job, deal_negotiation, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    DealService.first_sign_deal(deal_id=deal_negotiation.id, user_id=worker_user.id, db=db)

    assert deal_negotiation.worker_signed_at is not None
    notification.assert_called_once()

# Успешная подпись с обеих сторон
def test_first_sign_both_success(db, mocker, worker_user, client_user, job, deal_negotiation, client_wallet, worker_wallet):
    mocker.patch("Business.Deals.deals_service.create_notification")

    deal_negotiation.client_signed_at = datetime.now(timezone.utc)
    db.commit()

    DealService.first_sign_deal(deal_id=deal_negotiation.id, user_id=worker_user.id, db=db)

    assert deal_negotiation.client_signed_at is not None
    assert deal_negotiation.is_fully_signed is True


# Ошибка что сделка не найдена
def test_first_sign_deal_not_found_fail(db, mocker, worker_user, client_user, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    with pytest.raises(HTTPException) as exc:
        DealService.first_sign_deal(deal_id=95435, user_id=client_user.id, db=db)

    assert exc.value.status_code == 404
    notification.assert_not_called()


# Ошибка со статусом
def test_first_sign_deal_status_fail(db, mocker, worker_user, client_user, deal_negotiation, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    deal_negotiation.status = DealStatus.ACTIVE
    db.commit()

    with pytest.raises(HTTPException) as exc:
        DealService.first_sign_deal(deal_id=deal_negotiation.id, user_id=client_user.id, db=db)

    assert exc.value.status_code == 400
    notification.assert_not_called()

# Ошибка что это чужая сделка
def test_first_sign_deal_not_yours_fail(db, mocker, worker_user, client_user, deal_negotiation, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")

    deal_negotiation.client_id = 264
    db.commit()

    with pytest.raises(HTTPException) as exc:
        DealService.first_sign_deal(deal_id=deal_negotiation.id, user_id=client_user.id, db=db)

    assert exc.value.status_code == 405
    notification.assert_not_called()

# Ошибка что сделка уже подписана
def test_first_sign_deal_already_exists_fail(db, mocker, worker_user, client_user, deal_negotiation, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    days_2_ago = datetime.now(timezone.utc) - timedelta(days=2)

    deal_negotiation.client_signed_at = days_2_ago
    db.commit()

    with pytest.raises(HTTPException) as exc:
        DealService.first_sign_deal(deal_id=deal_negotiation.id, user_id=client_user.id, db=db)

    assert exc.value.status_code == 400
    notification.assert_not_called()
    


# =============================================================================================
# ==================== COMPLETE DEAL TESTS ===========================
# ===============================================================================================

# Подпись со стороны клиента
def test_complete_deal_success_client(db, mocker, worker_user, client_user, deal, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    mocker.patch("Business.Deals.deals_service.process_job_payment")

    message = "Сделка успешно подписана! Для завершения осталось подписать работнику"

    result = DealService.complete_deal(deal_id=deal.id, user_id=client_user.id, db=db)

    assert result["message"] == message
    assert deal.client_completed_at is not None
    notification.assert_called_once()


# Подпись о завершении со стороны работника
def test_complete_deal_success_worker(db, mocker, worker_user, client_user, deal, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    mocker.patch("Business.Deals.deals_service.process_job_payment")

    message = "Сделка успешно подписана! Для завершения осталось подписать клиенту"

    result = DealService.complete_deal(deal_id=deal.id, user_id=worker_user.id, db=db)

    assert result["message"] == message
    assert deal.worker_completed_at is not None
    notification.assert_called_once()


# Подпись о завершении с обеих сторон
def test_complete_deal_success_both(db, mocker, worker_user, client_user, deal, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    job_process = mocker.patch("Business.Deals.deals_service.process_job_payment")
    
    deal.client_completed_at = datetime.now(timezone.utc)
    db.commit()

    message = "Сделка успешно завершена с обеих сторон!"

    result = DealService.complete_deal(deal_id=deal.id, user_id=worker_user.id, db=db)

    assert result["message"] == message
    assert deal.worker_completed_at is not None
    assert deal.client_completed_at is not None
    assert deal.completed_at is not None
    assert client_wallet.balance == 20000
    assert worker_wallet.balance == 0
    notification.assert_not_called()
    job_process.assert_called_once()


# Ошибка что сделка не найдена
def test_complete_deal_not_found_fail(db, mocker, worker_user, client_user, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")

    with pytest.raises(HTTPException) as exc:
        DealService.complete_deal(deal_id=15000, user_id=client_user.id, db=db)

  
    assert exc.value.status_code == 404
    notification.assert_not_called()
    process_job.assert_not_called()

# Ошибка со статусом
def test_complete_deal_status_fail(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")

    deal.status = DealStatus.COMPLETED
    db.commit()

    with pytest.raises(HTTPException) as exc:
        DealService.complete_deal(deal_id=deal.id, user_id=client_user.id, db=db)

    assert exc.value.status_code == 405
    notification.assert_not_called()
    process_job.assert_not_called()


# Ошибка что чужая сделка
def test_complete_deal_not_yours_fail(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")

    with pytest.raises(HTTPException) as exc:
        DealService.complete_deal(deal_id=deal.id, user_id=15000, db=db)

    assert exc.value.status_code == 405
    notification.assert_not_called()
    process_job.assert_not_called()


# Ошибка что уже завершено со стороны клиента
def test_complete_deal_sign_exists_client_fail(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")

    deal.client_completed_at = datetime.now(timezone.utc)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        DealService.complete_deal(deal_id=deal.id, user_id=client_user.id, db=db)

    assert exc.value.status_code == 400
    notification.assert_not_called()
    process_job.assert_not_called()


# Ошибка что уже завершено со стороны работника
def test_complete_deal_sign_exists_worker_fail(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")

    deal.worker_completed_at = datetime.now(timezone.utc)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        DealService.complete_deal(deal_id=deal.id, user_id=worker_user.id, db=db)

    assert exc.value.status_code == 400
    notification.assert_not_called()
    process_job.assert_not_called()

# ==============================================================================
# ================================== CANCEL DEAL TESTS =======================
# ===================================================================================

# Успешная отмена сделки со стороны клиента
def test_cancel_deal_success_client(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")
    
    data = CancelDealSchema(reason="Test reason")

    result = DealService.cancel_deal(deal_id=deal.id, user_id=client_user.id, data=data, db=db)

    assert result is not None
    notification.assert_called_once()
    process_job.assert_called_once()
    assert client_wallet.balance == 20000
    assert worker_wallet.balance == 0
    assert deal.status == DealStatus.CANCELLED

# Успешная отмена сделки со стороны работника
def test_cancel_deal_success_worker(db, mocker, worker_user, client_user, job, deal, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")
    
    data = CancelDealSchema(reason="Test reason")

    result = DealService.cancel_deal(deal_id=deal.id, user_id=worker_user.id, data=data, db=db)

    assert result is not None
    notification.assert_called_once()
    process_job.assert_called_once()
    assert client_wallet.balance == 20000 
    assert worker_wallet.balance == 0
    assert deal.status == DealStatus.CANCELLED

# Ошибка что сделка не найдена
def test_cancel_deal_not_found_fail(db, mocker, worker_user, client_user, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")
    
    data = CancelDealSchema(reason="Test reason")
    with pytest.raises(HTTPException) as exc:
        DealService.cancel_deal(deal_id=15000, user_id=worker_user.id, data=data, db=db)
    
    assert exc.value.status_code == 404
    notification.assert_not_called()
    process_job.assert_not_called()

# Ошибка что чужая сделка
def test_cancel_deal_not_yours_fail(db, mocker, worker_user, client_user, deal, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")
    
    data = CancelDealSchema(reason="Test reason")
    with pytest.raises(HTTPException) as exc:
        DealService.cancel_deal(deal_id=deal.id, user_id=15000, data=data, db=db)
    
    assert exc.value.status_code == 403
    notification.assert_not_called()
    process_job.assert_not_called()

# Ошибка со статусом
def test_cancel_deal_status_fail(db, mocker, worker_user, client_user, deal, job, client_wallet, worker_wallet):
    notification = mocker.patch("Business.Deals.deals_service.create_notification")
    process_job = mocker.patch("Business.Deals.deals_service.process_job_payment")

    deal.status = DealStatus.COMPLETED
    db.commit()

    data = CancelDealSchema(reason="Test reason")
    with pytest.raises(HTTPException) as exc:
        DealService.cancel_deal(deal_id=deal.id, user_id=client_user.id, data=data, db=db)
    
    assert exc.value.status_code == 400
    notification.assert_not_called()
    process_job.assert_not_called()




