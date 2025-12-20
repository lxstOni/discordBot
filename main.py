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
    debug_guilds=[1427289795931144334],
    status=status
)


def log_folder_exist():
    folder_path = '../log/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Nested folders '{folder_path}' created.")
    else:
        print(f"Nested folders '{folder_path}' already exist.")

if __name__ == "__main__":
    bot.load_cogs("cogs")
    settings.setup_logger()
    bot.run(os.getenv("TOKEN"))
