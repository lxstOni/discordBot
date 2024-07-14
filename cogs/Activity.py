import discord
import ezcord
from discord.commands import slash_command, Option
from discord.ext import commands


class Activity(ezcord.Cog, emoji="🧘"):

    @slash_command(description="Owner Only Command")
    @commands.is_owner()
    async def activity(
            self, ctx,
            typ: Option(str, choices=["game", "stream"]),
            name: Option(str)
    ):
        if typ == "game":
            act = discord.Game(name=name)
        else:
            act = discord.Streaming(
                name=name,
                url="https://www.twitch.tv/keks"
            )

        await self.bot.change_presence(activity=act, status=discord.Status.dnd)
        await ctx.respond("Status was changed!")


def setup(bot):
    bot.add_cog(Activity(bot))