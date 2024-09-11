import os
from dotenv import load_dotenv
from src.utils.general import build_logger_config


dotenv_path = os.getenv("MIM_DOTENV", os.path.join(os.path.dirname(__file__), ".env"))

load_dotenv(dotenv_path, override=False)  # priorizes env vars (not .env file)

config = {
    "SQLALCHEMY_DATABASE_PREFIX": os.getenv("SQLALCHEMY_DATABASE_PREFIX", ""),
    "SQLALCHEMY_DATABASE_URL": os.getenv("SQLALCHEMY_DATABASE_URL", ""),
    "SQLALCHEMY_DATABASE_ECHO": os.getenv("SQLALCHEMY_DATABASE_ECHO", "").lower() in ('true', '1', 't'),
    "DATABASE_TABLE_METRICS": os.getenv("DATABASE_TABLE_METRICS", ""),
}