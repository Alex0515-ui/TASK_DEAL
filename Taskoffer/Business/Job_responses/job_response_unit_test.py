import pytest
from pytest_mock import mocker
from fastapi import HTTPException

from Core.entities.models import *
from Business.Job_responses.job_response_schema import CreateJobResponseSchema
from Business.Job_responses.job_responses_service import JobResponseService

# Успешное создание заявки на работу
def test_create_response_success(job_for_response, mocker, db, worker_user):
    mocker.patch("Business.Job_responses.job_responses_service.check_daily_limit_responses", return_value=False)
    mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    job_for_response.status = Job_status.IN_SEARCH
    db.commit()

    data = CreateJobResponseSchema(job_id=job_for_response.id, offered_price=15000, cover_letter="Hello")

    result = JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)

    assert result is not None
    assert result.worker_id == worker_user.id


# Ошибка при превышении лимита
def test_create_response_limit_fail(job_for_response, mocker, db, worker_user, client_user):
    mocker.patch("Business.Job_responses.job_responses_service.check_daily_limit_responses", return_value=True)
    mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    job_for_response.status = Job_status.IN_SEARCH
    db.commit()

    data = CreateJobResponseSchema(job_id=job_for_response.id, offered_price=15000, cover_letter="Hello")
    with pytest.raises(HTTPException) as exc:
        JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)

    assert exc.value.status_code == 403


# Ошибка что работа не найдена
def test_create_response_not_found_fail( mocker, db, worker_user):
    mocker.patch("Business.Job_responses.job_responses_service.check_daily_limit_responses", return_value=False)
    mocker.patch("Business.Job_responses.job_responses_service.create_notification")


    data = CreateJobResponseSchema(job_id=99999, offered_price=15000, cover_letter="Hello")
    with pytest.raises(HTTPException) as exc:
        JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)

    assert exc.value.status_code == 404

    
# Ошибка что нельзя на свою работу откликаться
def test_create_response_yourself_fail(job_for_response, mocker, db, worker_user):
    mocker.patch("Business.Job_responses.job_responses_service.check_daily_limit_responses", return_value=False)
    mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    job_for_response.status = Job_status.IN_SEARCH
    job_for_response.owner_id = worker_user.id
    db.commit()

    data = CreateJobResponseSchema(job_id=job_for_response.id, offered_price=15000, cover_letter="Hello")
    with pytest.raises(HTTPException) as exc:
        JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)

    assert exc.value.status_code == 400


# Ошибка со статусом
def test_create_response_status_fail(job_for_response, mocker, db, worker_user):
    mocker.patch("Business.Job_responses.job_responses_service.check_daily_limit_responses", return_value=False)
    mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    data = CreateJobResponseSchema(job_id=job_for_response.id, offered_price=15000, cover_letter="Hello")

    job_for_response.status = Job_status.ACCEPTED
    db.commit()

    with pytest.raises(HTTPException) as exc:
        JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)

    assert exc.value.status_code == 403


# Ошибка что уже оставлял заявку
def test_create_response_already_exists_fail(job_for_response, mocker, db, worker_user):
    mocker.patch("Business.Job_responses.job_responses_service.check_daily_limit_responses", return_value=False)
    mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    response_one = JobResponse(job_id=job_for_response.id, worker_id=worker_user.id, status=Response_status.PENDING)
    job_for_response.status = Job_status.IN_SEARCH
    job_for_response.owner_id = worker_user.id

    db.add(response_one)
    db.commit()

    data = CreateJobResponseSchema(job_id=job_for_response.id, offered_price=15000, cover_letter="Hello")
    with pytest.raises(HTTPException) as exc:
        JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)

    assert exc.value.status_code == 400


# =========================================================================================
# ================================ ACCEPT RESPONSE TESTS ====================================
# =========================================================================================================

# Успешное принятие заявки
def test_accept_response_success(job_for_response, response, mocker, db, worker_user, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")
    create_deal = mocker.patch("Business.Job_responses.job_responses_service.DealService.createDeal")

    response_one = JobResponse(job_id=job_for_response.id, worker_id=15, status=Response_status.PENDING)
    response_two = JobResponse(job_id=job_for_response.id, worker_id=16, status=Response_status.PENDING)

    db.add_all([response_one, response_two])
    db.commit()

    result = JobResponseService.accept_response(db=db, response_id=response.id, client_id=client_user.id)

    assert result['message'] == "Работник назначен, теперь работа начнется!"
    assert notification.call_count == 3
    create_deal.assert_called_once()

# Успешное принятие заявки с другой ценой
def test_accept_response_off_price_success(job_for_response, response, mocker, db, worker_user, client_user, client_wallet):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")
    create_deal = mocker.patch("Business.Job_responses.job_responses_service.DealService.createDeal")

    response_one = JobResponse(job_id=job_for_response.id, worker_id=15, status=Response_status.PENDING)
    response_two = JobResponse(job_id=job_for_response.id, worker_id=16, status=Response_status.PENDING)

    db.add_all([response_one, response_two])

    response.offered_price = 16000
    db.commit()

    result = JobResponseService.accept_response(db=db, response_id=response.id, client_id=client_user.id)

    assert result['message'] == "Работник назначен, теперь работа начнется!"
    assert notification.call_count == 3
    create_deal.assert_called_once()
    assert client_wallet.balance == 19000

# Ошибка что заявка не найдена
def test_accept_response_not_found_fail(job_for_response, mocker, db, worker_user, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")
    create_deal = mocker.patch("Business.Job_responses.job_responses_service.DealService.createDeal")

    with pytest.raises(HTTPException) as exc:
        JobResponseService.accept_response(db=db, response_id=99999, client_id=client_user.id)

    assert exc.value.status_code == 404

# Ошибка что работа не найдена
def test_accept_response_job_not_found_fail(job_for_response, mocker, db, response, worker_user, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")
    create_deal = mocker.patch("Business.Job_responses.job_responses_service.DealService.createDeal")

    db.delete(job_for_response)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        JobResponseService.accept_response(db=db, response_id=response.id, client_id=client_user.id)

    assert exc.value.status_code == 404
    notification.assert_not_called()
    create_deal.assert_not_called()


# Ошибка что чужая работа
def test_accept_response_not_yours_fail(job_for_response, mocker, db, response, worker_user, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")
    create_deal = mocker.patch("Business.Job_responses.job_responses_service.DealService.createDeal")

    with pytest.raises(HTTPException) as exc:
        JobResponseService.accept_response(db=db, response_id=response.id, client_id=99999)

    assert exc.value.status_code == 403
    notification.assert_not_called()
    create_deal.assert_not_called()


# Ошибка что у работы уже есть работник
def test_accept_response_already_has_fail(job_for_response, mocker, db, response, worker_user, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")
    create_deal = mocker.patch("Business.Job_responses.job_responses_service.DealService.createDeal")

    job_for_response.worker_id = 15
    db.commit()

    with pytest.raises(HTTPException) as exc:
        JobResponseService.accept_response(db=db, response_id=response.id, client_id=client_user.id)

    assert exc.value.status_code == 400
    notification.assert_not_called()
    create_deal.assert_not_called()

# Ошибка что при другой цене не хватает средств в кошельке
def test_accept_response_not_enough_money_fail(job_for_response, mocker, db, response, worker_user, client_user, client_wallet):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")
    create_deal = mocker.patch("Business.Job_responses.job_responses_service.DealService.createDeal")

    job_for_response.worker_id = 15
    response.offered_price = 60000
    db.commit()

    with pytest.raises(HTTPException) as exc:
        JobResponseService.accept_response(db=db, response_id=response.id, client_id=client_user.id)

    assert exc.value.status_code == 400
    assert client_wallet.balance == 20000
    notification.assert_not_called()
    create_deal.assert_not_called()


# =========================================================================================
# =============================== REJECT RESPONSE TESTS ======================================
# =====================================================================================

# Успешное отклонение заявки
def test_reject_response_success(db, mocker, response, job_for_response, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    result = JobResponseService.reject_response(db=db, response_id=response.id, client_id=client_user.id)

    assert result['message'] == "Заявка успешно отклонена"

    notification.assert_called_once()

# Ошибка что заявка не найдена
def test_reject_response_not_found_fail(db, mocker, response, job_for_response, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    with pytest.raises(HTTPException) as exc:
        JobResponseService.reject_response(db=db, response_id=99999, client_id=client_user.id)

    assert exc.value.status_code == 404
    notification.assert_not_called()


# Ошибка что чужая работа
def test_reject_response_not_yours_fail(db, mocker, response, job_for_response, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    with pytest.raises(HTTPException) as exc:
        JobResponseService.reject_response(db=db, response_id=response.id, client_id=99999)

    assert exc.value.status_code == 403
    notification.assert_not_called()


# Ошибка что работа не найдена
def test_reject_response_job_not_found_fail(db, mocker, response, job_for_response, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    db.delete(job_for_response)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        JobResponseService.reject_response(db=db, response_id=response.id, client_id=client_user.id)

    assert exc.value.status_code == 404
    notification.assert_not_called()


# Ошибка со статусом работы (завершена)
def test_reject_response_job_status_fail(db, mocker, response, job_for_response, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    job_for_response.status = Job_status.DONE
    db.commit()

    with pytest.raises(HTTPException) as exc:
        JobResponseService.reject_response(db=db, response_id=response.id, client_id=client_user.id)

    assert exc.value.status_code == 400
    notification.assert_not_called()
    

# Ошибка со статусом работы (отменена)
def test_reject_response_status_fail(db, mocker, response, job_for_response, client_user):
    notification = mocker.patch("Business.Job_responses.job_responses_service.create_notification")

    job_for_response.status = Job_status.CANCELLED
    db.commit()

    with pytest.raises(HTTPException) as exc:
        JobResponseService.reject_response(db=db, response_id=response.id, client_id=client_user.id)

    assert exc.value.status_code == 400
    notification.assert_not_called()







