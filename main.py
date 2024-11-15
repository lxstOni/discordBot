import discord
import ezcord
import os
from dotenv import load_dotenv
from source.settings import settings



load_dotenv()
status = discord.Status.dnd


bot = ezcord.Bot(
    intents=discord.Intents.all(),
    language="de",
    debug_guilds=[1305837473535885324],
    status=status
)
bot.add_help_command()

if __name__ == "__main__":
    bot.load_cogs("cogs")
    settings.setup_logger()
    bot.run(os.getenv("TOKEN"))
