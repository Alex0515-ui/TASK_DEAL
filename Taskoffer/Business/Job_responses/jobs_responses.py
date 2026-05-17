from fastapi import APIRouter
from Core.auth.authentication import db_dependency, user_dependency
from Business.Job_responses.job_response_schema import CreateJobResponseSchema, DeleteJobResponseSchema
from Business.Job_responses.job_responses_service import JobResponseService
from Core.entities.models import *


router = APIRouter(prefix="/job_responses")


# Создание заявки на работу
@router.post("/bind")
def create_job_response(data: CreateJobResponseSchema, db: db_dependency, user: user_dependency):

    return JobResponseService.create_bind_response(data=data, db=db, worker_id=user['id'])

# Принятие заявки
@router.patch("/accept/{id}")
def accept_worker_response(id: int, db: db_dependency, user: user_dependency):
    return JobResponseService.accept_response(db=db, response_id=id, client_id=user['id'])


# Получение всех заявок на свои работы
@router.get("/")
def get_job_responses(
    db: db_dependency, 
    user: user_dependency, 
    response_status: Response_status = None,
    type: Job_type = None, 
    job_id: int = None,
    offset: int = 0, 
    limit: int = 10
):
    return JobResponseService.get_my_client_responses(
        db=db, client_id=user['id'], type=type, job_id=job_id,
        response_status=response_status, offset=offset, limit=limit
    )

# Получение своих оставленных заявок
@router.get("/my")
def get_my_worker_responses(
    db: db_dependency, 
    user: user_dependency,
    type: Job_type = None,
    status: Job_status = None,
    response_status: Response_status = None,
    offset: int = 0,
    limit: int = 10
):
    return JobResponseService.get_my_worker_responses(
        db=db, worker_id=user['id'], type=type, job_status=status, 
        response_status=response_status, offset=offset, limit=limit
    )

# Получение своей заявки работника
@router.get("/my/{id}")
def get_my_response(id: int, db: db_dependency, user: user_dependency):
    return JobResponseService.get_worker_response(db=db, response_id=id, worker_id=user['id'])

# Получение заявки работника кандидата
@router.get("/job/response/{id}")
def get_response(id: int, db: db_dependency, user: user_dependency):
    return JobResponseService.get_client_response(db=db, response_id=id, client_id=user['id'])

# Отклонение заявки
@router.patch("/job/response/{id}")
def reject_job_response(id: int, db: db_dependency, user: user_dependency):
    return JobResponseService.reject_response(db=db, response_id=id, client_id=user['id'])


@router.delete("/delete/{response_id}")
def delete_job_response(response_id: int, data: DeleteJobResponseSchema,db: db_dependency, user: user_dependency):
    return JobResponseService.delete_response(db=db, response_id=response_id, worker_id=user['id'], job_id=data.job_id)



