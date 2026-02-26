import discord
import ezcord
from discord.commands import slash_command
import requests


class ServerCalender(ezcord.Cog, emoji="🗓️", description="seh Calender einträge für deinen Server"):
    pass

def setup(bot):
    bot.add_cog(Memes(bot))