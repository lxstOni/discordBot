import discord
import ezcord
from discord.commands import slash_command


class Clear(ezcord.Cog, emoji="🗑️"):
    @slash_command(description="Clear Messages")
    async def clear(self,ctx:discord.ApplicationContext):
        await ctx.channel.purge(limit=None)

def setup(bot):
    bot.add_cog(Clear(bot))