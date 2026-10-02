import os
import discord
from discord.ext import commands

# Configure bot intents (permissions for event handling)
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )

    async def setup_hook(self):
        """Runs before the bot starts connecting to Discord."""
        print("Initializing bot setup...")

    async def on_ready(self):
        """Triggered when the bot successfully logs in."""
        print(f"Logged in successfully as {self.user} (ID: {self.user.id})")
        print("Bot is ready to accept commands.")

    async def on_message(self, message: discord.Message):
        """Processes incoming messages."""
        # Prevent the bot from responding to its own messages
        if message.author.bot:
            return

        # Process registered commands
        await self.process_commands(message)

    def run(self):
        """Retrieves token from environment variables and launches the bot."""
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError(
                "DISCORD_TOKEN environment variable is not set. "
                "Please add it to your environment or .env file."
            )
        super().run(token)


# Basic example command: !ping
@commands.command(name="ping")
async def ping(ctx: commands.Context):
    """Responds with 'Pong!' and latency."""
    latency = round(ctx.bot.latency * 1000)
    await ctx.send(f"Pong! 🏓 ({latency}ms)")


# Attach command to the bot class instance before export
Bot.add_command(ping)
