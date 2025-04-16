import asyncio
from model.model import Model
from pathlib import Path
from dotenv import load_dotenv
from os import getenv

import logging

log_file = Path(__file__).parent / "logs.log"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(level=logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

env_file = Path(__file__).parent / "model/.env"
load_dotenv(env_file)
CHAT_MODEL = getenv("CHAT_MODEL")
IMAGE_MODEL = getenv("IMAGE_MODEL")
INITIAL_PROMPT = getenv("INITIAL_PROMPT")

async def main():
    logger.info("Создан новый чат")
    conversation = Model(CHAT_MODEL, IMAGE_MODEL, INITIAL_PROMPT, logger)
    while True:
        user_input = input("User: \n")
        if user_input.lower() == 'exit':
            print("\nGoodbye!")
            break
        elif user_input.lower() == 'изображение':
            url = await conversation.image()
            if len(url) > 0:
                print(url)
        else:
            await conversation.response(user_input)

if __name__ == "__main__":
    asyncio.run(main())