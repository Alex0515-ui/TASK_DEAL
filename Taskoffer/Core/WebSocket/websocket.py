from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import jwt
from starlette.concurrency import run_in_threadpool
import logging


from Interactions.Messages.message_service import MessageService
from Core.config.database import SessionLocal
from Core.entities.models import *
from Core.config.configuration import settings
from Interactions.Messages.message_schema import CreateMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/websocket")

# Менеджер соединений WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections : dict[int, list[WebSocket]] = {}

    # Подключение
    async def connect(self, deal_id: int, websocket: WebSocket):
        await websocket.accept()
        if deal_id not in self.active_connections:
            self.active_connections[deal_id] = []
        self.active_connections[deal_id].append(websocket)

    # Отключение
    def disconnect(self, deal_id: int, websocket: WebSocket):
        self.active_connections[deal_id].remove(websocket)

        if not self.active_connections[deal_id]:
            del self.active_connections[deal_id]

    # Трансляция
    async def broadcast(self, deal_id: int, message: dict):
        for connection in self.active_connections.get(deal_id, []):
            await connection.send_json(message)


manager = ConnectionManager()

# ОСНОВНОЙ ЭНДПОИНТ realtime чата
@router.websocket("/ws/chat/{deal_id}")
async def websocket_endpoint(deal_id: int, websocket: WebSocket):

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        decoded_data = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = decoded_data.get("id")

    except:
        await websocket.close(code=1008)
        return

    db = SessionLocal()

    try:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            await websocket.close(code=1008)
            return

        if user_id not in [deal.client_id, deal.worker_id]:
            await websocket.close(code=1008)
            return

        await manager.connect(deal_id, websocket)

        while True:

            text = await websocket.receive_text()

            new_message = await run_in_threadpool(MessageService.create_message, deal_id, user_id, CreateMessage(text=text), db)

            await manager.broadcast(
                deal_id,
                {
                    "text": new_message.text,
                    "sender_id": user_id
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(deal_id, websocket)

    except Exception as e:
        logger.error(f"ERROR: {e}")
        await websocket.close(1011)
    

    finally:
        db.close()