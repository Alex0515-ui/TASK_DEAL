from fastapi import FastAPI
from Core.config.database import Base, engine
from tasks import scheduler
from contextlib import asynccontextmanager
import logging

import Core.auth.authentication as authentication
import Business.Jobs.jobs as job
import Business.Job_responses.jobs_responses as job_responses
import Business.Deals.deals as deals
import Interactions.Reviews.reviews as reviews
import Interactions.Messages.messages as messages
import Core.WebSocket.websocket as websocket
import Interactions.Notifications.notifications as nots
import Interactions.Payment.payment as payment


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Жизненный цикл приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    if not scheduler.running:
        scheduler.start()
        logger.info("Планировщик приступил к работе")

    yield

    scheduler.shutdown()
    logger.info("Планировщик вырублен")


app = FastAPI(lifespan=lifespan)

# Роутеры 
app.include_router(authentication.router)
app.include_router(job.router)
app.include_router(job_responses.router)
app.include_router(deals.router)
app.include_router(reviews.router)
app.include_router(messages.router)
app.include_router(websocket.router)
app.include_router(nots.router)
app.include_router(payment.router)

Base.metadata.create_all(bind=engine)






