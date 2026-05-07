from fastapi import APIRouter

from auth.authentication import db_dependency, user_dependency
from entities.models import *
from Messages.message_service import MessageService
from Messages.message_schema import CreateMessage


router = APIRouter(prefix="/messages")



@router.post("/{deal_id}/create")
def create_message(deal_id: int, user: user_dependency, message: CreateMessage, db: db_dependency):
    return MessageService.create_message(deal_id=deal_id, sender_id=user['id'], message=message, db=db)

@router.get("/{deal_id}/all")
def get_chat_messages(deal_id: int, user: user_dependency, db: db_dependency, offset: int = 0, limit: int = 10):
    return MessageService.get_messages(deal_id=deal_id, user_id=user['id'], db=db, offset=offset, limit=limit)

@router.patch("/{deal_id}/mark")
def mark_messages_as_read(deal_id: int, user: user_dependency, db: db_dependency):
    return MessageService.mark_as_read(deal_id=deal_id, user_id=user['id'], db=db)