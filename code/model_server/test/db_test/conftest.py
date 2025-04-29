import pytest
import pytest_asyncio
from testcontainers.mongodb import MongoDbContainer
from test.db_test.db import init_db

# MongoDB контейнер (синхронный, потому что Testcontainers не поддерживает async)
@pytest.fixture(scope="session")
def mongo_container():
    container = MongoDbContainer("mongo:5.0")
    container.start()
    yield container
    container.stop()


# Инициализация Motor-клиента и базы данных
@pytest_asyncio.fixture(scope="function")
async def test_db(mongo_container):
    uri = mongo_container.get_connection_url()
    db = init_db(uri, "test_db")
    await db["chats"].delete_many({})  # Очистка чатов перед тестом
    yield db