import os

import discord
import ezcord
from discord.commands import slash_command
from discord import  file



class Clear(ezcord.Cog, emoji="🗑️"):

    @slash_command(description="Clear Messages")
    async def clear(self, ctx: discord.ApplicationContext, amount: int):
        await ctx.channel.purge(limit=amount)

        image_path = 'data/Images/trash.gif'

        # Open the image file in binary mode
        with open(image_path, 'rb') as f:
            picture = discord.File(f)

        await ctx.respond("this message get cleared in 10 seconds ...",file=picture,ephemeral=True, delete_after=10)
        await ctx.followup.send(f"cleared {amount} messages", delete_after=10, ephemeral=True)

def setup(bot):
    bot.add_cog(Clear(bot))