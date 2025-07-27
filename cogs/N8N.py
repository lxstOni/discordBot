import discord
import ezcord
from discord.commands import slash_command, Option
from discord.ext import commands


class N8N(ezcord.Cog, emoji="🔄", description="(Owner) Automations and Server info", hidden=True):
    pass



def setup(bot):
    bot.add_cog(N8N(bot))