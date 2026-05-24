import pytest
from fastapi import HTTPException
from pytest_mock import mocker
from Core.entities.models import *
from Business.Jobs.job_service import JobService
from Business.Jobs.job_schemas import CreateJobSchema
from datetime import datetime, timezone, timedelta


# Успешное создание работы
def test_create_job_success(mocker, client_user, client_wallet, db):
    limit = mocker.patch("Business.Jobs.job_service.check_daily_limit_jobs", return_value=False)

    expire = datetime.now(timezone.utc) + timedelta(days=2)
    deadline = datetime.now(timezone.utc) + timedelta(days=7)

    data = CreateJobSchema(
        title="Test job", 
        description="Test desc job", 
        price=10000, 
        type=Job_type.REPAIR, 
        expires_at=expire, 
        deadline = deadline
    )

    result = JobService.create_job(job_data=data, owner_id=client_user.id, db=db)

    assert result is not None
    assert client_wallet.balance == 10000


# Ошибка что лимит превышен
def test_create_job_limit_fail(mocker, client_user, client_wallet, db):
    limit = mocker.patch("Business.Jobs.job_service.check_daily_limit_jobs", return_value=True)
    process_job = mocker.patch("Business.Jobs.job_service.process_job_payment")

    expire = datetime.now(timezone.utc) + timedelta(days=2)
    deadline = datetime.now(timezone.utc) + timedelta(days=7)

    data = CreateJobSchema(
        title="Test job", 
        description="Test desc job", 
        price=10000, 
        type=Job_type.REPAIR, 
        expires_at=expire, 
        deadline = deadline
    )
    with pytest.raises(HTTPException) as exc:
        JobService.create_job(job_data=data, owner_id=client_user, db=db)

    assert exc.value.status_code == 403
    process_job.assert_not_called()


# ===================================================================================================
# ================================ CANCEL JOB TESTS ===================================================
# ==================================================================================================

# Успешная отмена при наличии работника
def test_cancel_job_with_worker_success(mocker, job, client_user, db, deal, client_wallet):
    notification = mocker.patch("Business.Jobs.job_service.create_notification")

    result = JobService.cancel_job(job_id=job.id, owner_id=client_user.id, db=db)

    assert result.status == Job_status.CANCELLED
    assert deal.status == DealStatus.CANCELLED
    assert client_wallet.balance == 35000
    
    notification.assert_called_once()

# Успешная отмена без работника
def test_cancel_job_without_worker_success(mocker, job, client_user, db, client_wallet):
    notification = mocker.patch("Business.Jobs.job_service.create_notification")

    job.worker_id = None
    db.commit()

    result = JobService.cancel_job(job_id=job.id, owner_id=client_user.id, db=db)

    assert result.status == Job_status.CANCELLED
    assert client_wallet.balance == 35000
    notification.assert_not_called()



# Ошибка что работа не найдена
def test_cancel_job_not_found_fail(mocker, job, client_user, db, client_wallet):
    notification = mocker.patch("Business.Jobs.job_service.create_notification")
    process_job = mocker.patch("Business.Jobs.job_service.process_job_payment")

    with pytest.raises(HTTPException) as exc:
        JobService.cancel_job(job_id=99999, owner_id=client_user.id, db=db)

    assert exc.value.status_code == 404
    assert client_wallet.balance == 20000
    process_job.assert_not_called()
    notification.assert_not_called()


# Ошибка что работа уже отменена
def test_cancel_job_already_cancelled_fail(mocker, job, client_user, db, client_wallet):
    notification = mocker.patch("Business.Jobs.job_service.create_notification")
    process_job = mocker.patch("Business.Jobs.job_service.process_job_payment")

    job.status = Job_status.CANCELLED
    db.commit()

    with pytest.raises(HTTPException) as exc:
        JobService.cancel_job(job_id=job.id, owner_id=client_user.id, db=db)

    assert exc.value.status_code == 403
    assert client_wallet.balance == 20000
    process_job.assert_not_called()
    notification.assert_not_called()


# Ошибка что работа уже завершена
def test_cancel_job_already_completed_fail(mocker, job, client_user, db, client_wallet):
    notification = mocker.patch("Business.Jobs.job_service.create_notification")
    process_job = mocker.patch("Business.Jobs.job_service.process_job_payment")

    job.status = Job_status.DONE
    db.commit()

    with pytest.raises(HTTPException) as exc:
        JobService.cancel_job(job_id=job.id, owner_id=client_user.id, db=db)

    assert exc.value.status_code == 400
    assert client_wallet.balance == 20000
    process_job.assert_not_called()
    notification.assert_not_called()


