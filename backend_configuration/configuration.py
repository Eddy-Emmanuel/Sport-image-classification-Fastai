from os import getenv
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(".env")

class Config(BaseSettings):
    HOMEPAGE_TITLE : str = getenv("HOMEPAGE_TITLE")
    OPENAPI_URL : str = getenv("OPENAPI_URL")
    CONNECT_ARGS : str = getenv("CONNECT_ARGS")
    DATABASE_URL : str = getenv("DATABASE_URL")
    ALGORITHM : str = getenv("ALGORITHM")
    SECRET_KEY: str = getenv("SECRET_KEY")

