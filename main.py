import discord
import ezcord
import os
from dotenv import load_dotenv

load_dotenv()
status = discord.Status.dnd



bot = ezcord.Bot(
    intents=discord.Intents.all(),
    language="de",
    debug_guilds=[1092275892090327113],
    status=status
)
bot.add_help_command()

if __name__ == "__main__":
    bot.load_cogs("cogs")
    bot.run(os.getenv("TOKEN"))