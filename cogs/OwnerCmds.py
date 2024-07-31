import discord
import ezcord
from discord.commands import slash_command, Option
from discord.ext import commands


class OwnerCmds(ezcord.Cog, emoji="🔑", description="Bot Owner only Commands", hidden=True):

    @slash_command(description="Owner Only Command")
    @commands.is_owner()
    async def activity(
            self, ctx,
            typ: Option(str, choices=["game", "stream"]),
            name: Option(str)
    ):
        if typ == "game":
            activity = discord.Game(name=name)
        else:
            activity = discord.Streaming(
                name=name,
                url="https://discord.com/invite/jBQXd22yfe"
            )

        await self.bot.change_presence(activity=activity, status=discord.Status.dnd)
        await ctx.respond("Status was changed!")


def setup(bot):
    bot.add_cog(OwnerCmds(bot))