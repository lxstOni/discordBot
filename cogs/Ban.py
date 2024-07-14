import discord
from discord.ext import commands
from discord.commands import slash_command
import ezcord


class Ban(ezcord.Cog,emoji="🚫"):
    @slash_command(description="Ban a user")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member):
        await ctx.guild.ban(member)
        ban_embed = discord.Embed(
            color=discord.Color.red(),
            description=f"{member.mention} got banned"
        )
        ban_embed.set_thumbnail(url=member.display_avatar)
        ban_embed.set_image(url="https://media1.giphy.com/media/hSXiJbWunRqZMr0KTE/giphy.gif?cid=ecf05e47c1tyzvsa9muz9l7y4m2hitfojqoqbjw8p393qcgk&ep=v1_gifs_search&rid=giphy.gif&ct=g")
        ban_embed.set_footer(text=f"Embed created from {self.bot.user}")

        await ctx.respond(embed=ban_embed, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Ban(bot))