import discord
import ezcord
import os
from dotenv import load_dotenv
from cogs.Ticket import CreateTicketButton

load_dotenv()

bot = ezcord.Bot(
    intents=discord.Intents.all(),
    language="de",
    debug_guilds=[1092275892090327113]
)





if __name__ == "__main__":
    bot.load_cogs("cogs")
    bot.run(os.getenv("TOKEN"))