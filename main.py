import discord
import ezcord
import os
from dotenv import load_dotenv
import logging

load_dotenv()
status = discord.Status.dnd

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename="log/discord.log", encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

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