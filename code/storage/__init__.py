from dotenv import load_dotenv
from pathlib import Path
from os import getenv
from .mongo_async import MongoDB

env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)
DATABASE_USERNAME = getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = getenv("DATABASE_PASSWORD")
DATABASE_HOST = getenv("DATABASE_HOST")
DATABASE_PORT = getenv("DATABASE_PORT")

mongodb = MongoDB(DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)