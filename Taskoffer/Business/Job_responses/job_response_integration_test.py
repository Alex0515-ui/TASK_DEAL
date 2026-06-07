from fastapi.testclient import TestClient
from datetime import timedelta 
from main import app
from Core.auth.auth_methods import create_access_token
from Business.Jobs.job_models import Job_status
from Business.Job_responses.job_responses_service import JobResponseService
from Business.Job_responses.job_response_schema import CreateJobResponseSchema

client = TestClient(app)


# ======================================================================
# ================== CREATE RESPONSE TESTS ===============================
# ============================================================================

# Успешное создание заявки
def test_create_response_integ_success(db, job, worker_user):
    token = create_access_token(email=worker_user.email, user_id=worker_user.id, expire_time=timedelta(minutes=30))
    
    job.status = Job_status.IN_SEARCH
    job.worker_id = None
    db.commit()

    response = client.post(f"/job_responses/bind",
    headers={
        "Authorization": f"Bearer {token}"
    },
    json={
        "job_id": job.id
    }
    )

    assert response.status_code == 200

# Ошибка авторизации
def test_create_response_integ_fail(db, client_user, worker_user, job):
    
    job.status = Job_status.IN_SEARCH
    job.worker_id = None
    db.commit()

    response = client.post(f"/job_responses/bind",
    headers={
        "Authorization": f"Bearer dwqdwdwd"
    },
    json={
        "job_id": job.id
    }
    )

    assert response.status_code == 401


# =======================================================================
# ===================== ACCEPT RESPONSE TESTS =============================
# ==============================================================================


# Успешное принятие заявки
def test_accept_response_integ_success(db, client_user, job, worker_user):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))
    
    job.status = Job_status.IN_SEARCH
    job.worker_id = None
    data = CreateJobResponseSchema(job_id=job.id)
    job_response = JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)
    db.commit()


    response = client.patch(f"/job_responses/accept/{job_response.id}",
    headers={
        "Authorization": f"Bearer {token}"
    }
    )

    assert response.status_code == 200
    assert job.worker_id == worker_user.id


# Ошибка авторизации
def test_accept_response_integ_fail(db, client_user, job, worker_user):    
    job.status = Job_status.IN_SEARCH
    job.worker_id = None
    data = CreateJobResponseSchema(job_id=job.id)
    job_response = JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)
    db.commit()


    response = client.patch(f"/job_responses/accept/{job_response.id}",
    headers={
        "Authorization": f"Bearer sfwefqwqqdd"
    }
    )

    assert response.status_code == 401

# ====================================================================
# ======================= REJECT RESPONSE TESTS ==========================
# ===========================================================================


# Успешное отклонение заявки
def test_reject_response_integ_success(db, client_user, job, worker_user):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))
    
    job.status = Job_status.IN_SEARCH
    job.worker_id = None
    data = CreateJobResponseSchema(job_id=job.id)
    job_response = JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)
    db.commit()


    response = client.patch(f"/job_responses/job/response/{job_response.id}",
    headers={
        "Authorization": f"Bearer {token}"
    }
    )

    assert response.status_code == 200
    assert job.worker_id != worker_user.id


# Ошибка авторизации
def test_reject_response_integ_fail(db, client_user, job, worker_user):    
    job.status = Job_status.IN_SEARCH
    job.worker_id = None
    data = CreateJobResponseSchema(job_id=job.id)
    job_response = JobResponseService.create_bind_response(data=data, db=db, worker_id=worker_user.id)
    db.commit()


    response = client.patch(f"/job_responses/job/response/{job_response.id}",
    headers={
        "Authorization": f"Bearer sfwefqwqqwdd"
    }
    )

    assert response.status_code == 401