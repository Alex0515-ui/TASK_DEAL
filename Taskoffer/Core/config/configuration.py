from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
import sys

# Проверяем тестируется ли приложение (Сделано для использования тестовой бд в тестах а не настоящей)
IS_TESTING = "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ

if not IS_TESTING:
    load_dotenv()

# Класс который позволяет брать переменные из env удобно
class Settings(BaseSettings):
    DB_URL:str
    JWT_SECRET_KEY:str
    ALGORITHM:str

    model_config = SettingsConfigDict(
        env_file=None if IS_TESTING else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        extra='ignore'
    )

settings = Settings()