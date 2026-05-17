from fastapi import APIRouter

from Core.auth.authentication import db_dependency, user_dependency
from Core.entities.models import *
from Interactions.Notifications.notification_service import *
from Interactions.Notifications.notification_schema import CreateNotification


router = APIRouter(prefix='/nots')


@router.get("/")
def get_all_nots(user: user_dependency, db: db_dependency, type: NotificationType | None = None, offset: int = 0, limit: int = 10):
    return get_notifications(user_id=user['id'], db=db, type=type, offset=offset, limit=limit)

