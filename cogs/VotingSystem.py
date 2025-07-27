import discord
import ezcord
from discord.commands import slash_command, Option
from discord.ext import commands


class VotingSystem(ezcord.Cog, emoji="🔑", description="Bot Owner only Commands", hidden=True):
    pass



def setup(bot):
    bot.add_cog(VotingSystem(bot))