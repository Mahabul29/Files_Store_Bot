import motor.motor_asyncio  # Use motor for async support
import os
from config import DB_URL, DB_NAME

# Initialize the Async MongoDB Client
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = dbclient[DB_NAME]
user_data = database['users']

async def present_user(user_id: int):
    """Check if a user exists in the database."""
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    """Add a new user if they don't already exist."""
    if not await present_user(user_id):
        await user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    """Retrieve all user IDs from the database."""
    user_ids = []
    async for doc in user_data.find():
        user_ids.append(doc['_id'])
    return user_ids

async def del_user(user_id: int):
    """Delete a user from the database."""
    await user_data.delete_one({'_id': user_id})
    return
    
