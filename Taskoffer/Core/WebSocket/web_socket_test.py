import pytest
from pytest_mock import mocker
from fastapi.testclient import TestClient
from datetime import timedelta
from websocket import WebSocketDisconnect

from main import app
from Core.auth.auth_methods import create_access_token
from Core.config.database import get_db
from Core.entities.models import *


@pytest.fixture(autouse=True)
def override_db(db):
    app.dependency_overrides[get_db] = lambda: db
    yield
    app.dependency_overrides.clear()

client = TestClient(app)

# Успешное подключение к чату 
def test_webcocket_success(client_user, deal, mocker, db):
    mocker.patch("Core.WebSocket.websocket.SessionLocal", return_value=db)
    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    with client.websocket_connect(url=f"/websocket/ws/chat/{deal.id}?token={token}") as websocket:
        assert websocket is not None


# Проверка отправки сообщения
def test_websocket_send_message_success(client_user, deal, mocker, db):
    mocker.patch("Core.WebSocket.websocket.SessionLocal", return_value=db)
    
    mock_message = Message(
        text="Test message",
        sender_id=client_user.id,
        deal_id=deal.id
    )
    mocker.patch(
        "Core.WebSocket.websocket.MessageService.create_message", 
        return_value=mock_message
    )

    token = create_access_token(email=client_user.email, user_id=client_user.id, expire_time=timedelta(minutes=30))

    with client.websocket_connect(f"/websocket/ws/chat/{deal.id}?token={token}") as websocket:
        websocket.send_text("Test message")
        
        data = websocket.receive_json()

        assert data['text'] == "Test message"
        assert data['sender_id'] == client_user.id



# Ошибка что нету токена
def test_websocket_no_token_fail(deal, mocker, db):
    mocker.patch("Core.WebSocket.websocket.SessionLocal", return_value=db)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/websocket/ws/chat/{deal.id}") as websocket:
            pass


# Ошибка что токен неверный
def test_websocket_invalid_token_fail(deal, mocker, db):
    mocker.patch("Core.WebSocket.websocket.SessionLocal", return_value=db)
    with pytest.raises(WebSocketDisconnect):    
        with client.websocket_connect(f"/websocket/ws/chat/{deal.id}token=wewddqwdwqdwd") as websocket:
            pass


