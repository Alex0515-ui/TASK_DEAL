from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from Core.config.configuration import settings


IS_TEST = settings.DB_URL.startswith("sqlite")

engine_kwargs = {}

if IS_TEST:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_timeout"] = 30

engine = create_engine(
    settings.DB_URL, 
    **engine_kwargs
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



