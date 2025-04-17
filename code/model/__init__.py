from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from logger import logger
from model.model import Model

env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)
CHAT_MODEL = getenv("CHAT_MODEL")
IMAGE_MODEL = getenv("IMAGE_MODEL")
IMAGE_GENERATION_PROMPT = getenv("IMAGE_GENERATION_PROMPT")

model = Model(CHAT_MODEL, IMAGE_MODEL, IMAGE_GENERATION_PROMPT, logger)