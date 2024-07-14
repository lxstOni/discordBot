import discord
import ezcord
from discord.commands import slash_command, Option
from discord.utils import basic_autocomplete

amount = [10, 25, 50,100]


class Clear(ezcord.Cog, emoji="🗑️"):

    @slash_command(description="Clear Messages")
    async def clear(self, ctx: discord.ApplicationContext, amount: Option(int, autocomplete=basic_autocomplete(amount))):
        await ctx.channel.purge(limit=amount)

        await ctx.respond(f"cleared {amount} messages", delete_after=10, ephemeral=True)

def setup(bot):
    bot.add_cog(Clear(bot))