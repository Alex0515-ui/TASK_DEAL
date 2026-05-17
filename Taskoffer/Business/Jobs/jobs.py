from fastapi import APIRouter

from Business.Jobs.job_service import JobService
from Core.auth.authentication import db_dependency, user_dependency
from Business.Jobs.job_schemas import CreateJobSchema
from Core.entities.models import *
from enum import Enum

router = APIRouter(prefix="/jobs", tags=["Jobs"])

class Modes(Enum):
    AVAILABLE = "available"
    CLIENT = "client"
    WORKER = "worker" 

# Создание работы
@router.post("/create")
def create_job(data: CreateJobSchema, db: db_dependency, user: user_dependency):

    return JobService.create_job(job_data=data, db=db, owner_id=user['id'])


# Получение одной работы
@router.get("/get/{id}")
def get_job(user: user_dependency, id: int, db: db_dependency):
    return JobService.get_job(user_id=user['id'], job_id=id, db=db)


@router.get("/")    
def get_all_jobs(
    db: db_dependency, 
    job_type: Job_type = None, 
    limit: int = 10, 
    offset: int = 0
    ):

    return JobService.get_available_jobs(db=db, job_type=job_type, offset=offset, limit=limit)


# Получение всех работ( Свои созданные / Свои назначенные / Просто просмотр ленты задач )
@router.get("/my")
def get_my_jobs(
    user: user_dependency, 
    db: db_dependency, 
    mode: Modes, 
    job_type: Job_type = None, 
    job_status: Job_status = None, 
    limit: int = 10, 
    offset: int = 0
    ):

    if mode == Modes.CLIENT:
        return JobService.get_client_jobs(owner_id=user['id'], db=db, job_type=job_type, status=job_status, offset=offset, limit=limit)
    
    elif mode == Modes.WORKER:
        return JobService.get_worker_assigned_jobs(worker_id=user['id'], db=db, job_type=job_type, status=job_status, offset=offset, limit=limit)
    
# Отмена задачи
@router.patch("/cancel/{id}")
def delete_job(id: int, db: db_dependency, user: user_dependency):
    return JobService.cancel_job(job_id=id, db=db, owner_id=user['id'])



