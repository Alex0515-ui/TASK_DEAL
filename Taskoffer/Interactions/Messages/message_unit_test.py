import pytest
from pytest_mock import mocker
from fastapi import HTTPException
from Interactions.Messages.message_service import MessageService, CreateMessage
from Core.entities.models import *

# Успешная отправка сообщения
def test_create_message_success(db, client_user, deal):
    message = CreateMessage(text="Hello")

    result = MessageService.create_message(deal_id=deal.id, sender_id=client_user.id, message=message, db=db)

    assert result is not None
    assert result.sender_id == client_user.id


# Сделка не найдена ошибка
def test_create_message_deal_not_found_fail(db, client_user, deal):
    message = CreateMessage(text="Hello")

    with pytest.raises(HTTPException) as exc:
        MessageService.create_message(deal_id=99999, sender_id=client_user.id, message=message, db=db)

    assert exc.value.status_code == 404


# Ошибка со статусом сделки
def test_create_message_deal_status_fail(db, client_user, deal):
    message = CreateMessage(text="Hello")

    deal.status = DealStatus.COMPLETED
    db.commit()

    with pytest.raises(HTTPException) as exc:
        MessageService.create_message(deal_id=deal.id, sender_id=client_user.id, message=message, db=db)

    assert exc.value.status_code == 403

# Ошибка что не ваша сделка
def test_create_message_permission_fail(db, deal):
    message = CreateMessage(text="Hello")

    with pytest.raises(HTTPException) as exc:
        MessageService.create_message(deal_id=deal.id, sender_id=99999, message=message, db=db)

    assert exc.value.status_code == 403

# =================================================================================
# ================= MARK_AS_READ TESTS ===================================
# ==============================================================================


# Прочитал сообщения успешно
def test_mark_read_success(deal, db, client_user, worker_user):
    message = Message(sender_id=worker_user.id, deal_id=deal.id, text="Hello test")
    message2 = Message(sender_id=worker_user.id, deal_id=deal.id, text="Hello test2")

    db.add_all([message, message2])
    db.commit()

    result = MessageService.mark_as_read(deal_id=deal.id, user_id=client_user.id, db=db)

    assert result['message'] == "Сообщения помечены как прочитанные"


# Ошибка сделка не найдена
def test_mark_read_success(db, client_user):

    with pytest.raises(HTTPException) as exc:
        MessageService.mark_as_read(deal_id=99999, user_id=client_user.id, db=db)

    assert exc.value.status_code == 404


# Ошибка что не твоя сделка
def test_mark_read_success(db, client_user, deal):

    with pytest.raises(HTTPException) as exc:
        MessageService.mark_as_read(deal_id=deal.id, user_id=99999, db=db)

    assert exc.value.status_code == 403

