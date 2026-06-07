from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from main import app
from Core.auth.auth_methods import create_access_token
from Business.Jobs.jobs import Modes
from Business.Jobs.job_models import Job_type

client = TestClient(app)

# ================================================================================
# ================== CREATE JOB TESTS ========================================
# ================================================================================

# Успешное создание работы
def test_create_job_integ_success(db, client_user, client_wallet):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))
    expires_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()


    response = client.post("/jobs/create", 
    headers={
        "Authorization": f"Bearer {token}"
    },
    json={
        "title": "Test title",
        "description": "Test desc",
        "price": 15000,
        "type": Job_type.REPAIR.value,
        "expires_at": expires_at,
        "deadline": deadline
    }
    )

    assert response.status_code == 200


# Ошибка авторизации
def test_create_job_integ_fail(db, client_user):
    expires_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()


    response = client.post("/jobs/create", 
    headers={
        "Authorization": f"Bearer wweqwqwqwe"
    },
    json={
        "title": "Test title",
        "description": "Test desc",
        "price": 15000,
        "type": Job_type.REPAIR.value,
        "expires_at": expires_at,
        "deadline": deadline
    }
    )

    assert response.status_code == 401

# ========================================================================
# =============== GET_JOB TESTS ================================
# ===============================================================


# Успешное получение работы
def test_get_my_job_integ_success(db, client_user, job):

    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    response = client.get(f"/jobs/get/{job.id}", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200

# Ошибка авторизации
def test_get_my_job_integ_fail(db, client_user, job):

    response = client.get(f"/jobs/get/{job.id}", headers={
        "Authorization": f"Bearer scaddwdwqdwq"
    })

    assert response.status_code == 401


# ============================================================
# ================= GET_MY_JOBS TESTS =====================
# ===================================================================

# Получение всех моих работ
def test_get_my_jobs_integ_success(db, client_user, job):
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    response = client.get("/jobs/my", headers={
        "Authorization": f"Bearer {token}",
        
    },
    params={
            "mode": Modes.CLIENT.value
    })

    assert response.status_code == 200

# Получение всех работ работника
def test_get_my_jobs_worker_integ_success(db, worker_user, job):
    token = create_access_token(email=worker_user.email, user_id=worker_user.id, expire_time=timedelta(minutes=30))

    response = client.get("/jobs/my", headers={
        "Authorization": f"Bearer {token}",
        
    },
    params={
            "mode": Modes.WORKER.value
    })

    assert response.status_code == 200

# Ошибка валидации
def test_get_my_jobs_integ_fail(db, client_user, job):

    response = client.get("/jobs/my", headers={
        "Authorization": f"Bearer qwwdwdwqd",
        
    },
    params={
            "mode": Modes.CLIENT.value
    })

    assert response.status_code == 401
