import discord
import ezcord
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
import logging.handlers



load_dotenv()
status = discord.Status.dnd

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=4 * 1024 * 1024,
    backupCount=3,  
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)


bot = ezcord.Bot(
    intents=discord.Intents.all(),
    language="de",
    debug_guilds=[1305837473535885324],
    status=status
)
bot.add_help_command()

if __name__ == "__main__":
    bot.load_cogs("cogs")
    bot.run(os.getenv("TOKEN"))
