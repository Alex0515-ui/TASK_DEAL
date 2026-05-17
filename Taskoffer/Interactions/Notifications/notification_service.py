from Core.entities.models import Notification, NotificationType
from sqlalchemy.orm import Session


# Создать уведомление от лица платформы 
def create_notification(user_id: int, text: str, type: NotificationType, db: Session, related_id: int | None = None):
    notification = Notification(user_id=user_id, text=text, type=type, related_id=related_id)

    db.add(notification)

    return notification

# Получить уведомления
def get_notifications(user_id: int, db: Session, type: NotificationType | None = None, offset: int = 0, limit: int = 20):
    notifications = db.query(Notification).filter(Notification.user_id == user_id)

    if type:
        notifications = notifications.filter(Notification.type == type)

    return notifications.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    

        