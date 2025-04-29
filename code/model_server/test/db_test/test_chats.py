import pytest
from bson import ObjectId
from datetime import datetime

@pytest.mark.asyncio
async def test_chat_crud(test_db):
    chats = test_db["chats"]

    user_id = ObjectId()
    chat = {
        "user_id": user_id,
        "title": "Test Chat",
        "messages": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    result = await chats.insert_one(chat)
    inserted_id = result.inserted_id

    found = await chats.find_one({"_id": inserted_id})
    assert found is not None
    assert found["title"] == "Test Chat"

    deleted = await chats.delete_one({"_id": inserted_id})
    assert deleted.deleted_count == 1