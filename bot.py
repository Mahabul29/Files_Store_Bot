import os
import sys
from pyromod import listen  # Enables pyromod monkeypatches for Pyrogram
from pyrogram import Client
from pymongo import MongoClient

class Bot(Client):
    def __init__(self):
        # Fetch configuration variables from environment
        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")
        bot_token = os.getenv("BOT_TOKEN")
        mongo_uri = os.getenv("MONGO_URI")

        # Basic environment variable validation
        if not all([api_id, api_hash, bot_token]):
            print("Error: Missing one of API_ID, API_HASH, or BOT_TOKEN in environment variables.")
            sys.exit(1)

        # Initialize Pyrogram Client
        super().__init__(
            name="TelegramBot",
            api_id=int(api_id),
            api_hash=api_hash,
            bot_token=bot_token,
            plugins=dict(root="plugins")  # Automatically load command files from /plugins directory if present
        )

        # Initialize MongoDB Connection
        if mongo_uri:
            try:
                self.mongo_client = MongoClient(mongo_uri)
                self.db = self.mongo_client["bot_database"]
                print("Connected to MongoDB successfully.")
            except Exception as e:
                print(f"Failed to connect to MongoDB: {e}")
                self.db = None
        else:
            print("Warning: MONGO_URI not set. Running without MongoDB.")
            self.db = None

    async def start(self):
        """Called when the bot starts up."""
        await super().start()
        me = await self.get_me()
        print(f"Bot started successfully as @{me.username} (ID: {me.id})")

    async def stop(self, *args):
        """Called when the bot shuts down."""
        await super().stop(*args)
        if hasattr(self, "mongo_client") and self.mongo_client:
            self.mongo_client.close()
            print("MongoDB connection closed.")
        print("Bot stopped.")


# Basic Pyrogram handler example using class method
@Client.on_message()
async def sample_handler(client, message):
    # Pass execution to standard plugins/handlers
    pass
    
