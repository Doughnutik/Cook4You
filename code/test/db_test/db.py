from motor.motor_asyncio import AsyncIOMotorClient

def init_db(uri: str, db_name: str):
    client = AsyncIOMotorClient(uri)
    return client[db_name]