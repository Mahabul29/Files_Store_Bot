import motor.motor_asyncio
from config import DB_URL, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.user_data = self.db['users']
        self.ban_data = self.db['banned_users'] # Collection for Ban Menu
        self.fsub_data = self.db['fsub_channels'] # Collection for Fsub Menu

    # --- User Management ---
    async def present_user(self, user_id: int):
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        await self.user_data.insert_one({'_id': user_id})
        return

    async def full_userbase(self):
        user_ids = []
        async for doc in self.user_data.find():
            user_ids.append(doc['_id'])
        return user_ids

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})
        return

    async def total_users_count(self):
        return await self.user_data.count_documents({})

    # --- Admin Management ---
    async def is_admin(self, user_id: int):
        # You can add logic here to check if a user is in an admin collection
        # For now, it returns False; add your admin list logic as needed
        return False

# Create the instance that settings.py is looking for
Seishiro = Database(DB_URL, DB_NAME)
