import discord
import ezcord
from discord.commands import slash_command, Option
from discord.utils import basic_autocomplete
from discord.ext import commands

clear_amount = [10, 25, 50,100,125,150]


class Moderation(ezcord.Cog,emoji="🕵️‍♂️", description="Moderation Commands", hidden=True):
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

    @slash_command(description="Clear Messages")
    async def clear(self, ctx: discord.ApplicationContext, amount: Option(int, autocomplete=basic_autocomplete(clear_amount))):
        await ctx.channel.purge(limit=amount)

        await ctx.respond(f"cleared {amount} messages", delete_after=10, ephemeral=True)

    @slash_command(description="Kick a user")
    async def kick(self, ctx, member: discord.Member):
        if ctx.author.guild_permissions.kick_members:
            await ctx.guild.kick(member)

            kick_embed = discord.Embed(
                color=discord.Color.red(),
                description=f"{member.mention} got kicked"
            )
            kick_embed.set_thumbnail(url=member.display_avatar)
            kick_embed.set_image(url="https://media1.tenor.com/m/5JmSgyYNVO0AAAAC/asdf-movie.gif")
            kick_embed.set_footer(text=f"Embed created from {self.bot.user}")

            await ctx.respond(embed=kick_embed, ephemeral=True)

    @slash_command(name="unban", description="Unbans the specified member.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, reason: Option(str, "Enter a reason for the unban", required=False, default='no reason given')):
        await ctx.guild.unban(user)

        unban_embed = discord.Embed(
            title="Success",
            description=f"{user.mention} has been unbanned.",
            color=discord.Color.green()
        )
        unban_embed.add_field(name="Reason", value=reason)
        unban_embed.set_thumbnail(url="https://media1.tenor.com/m/B3iUTS5HXAAAAAAC/quby-cute.gif")
        unban_embed.set_thumbnail(url=f"{user.display_avatar}")

        await ctx.response.send_message(embed=unban_embed, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Moderation(bot))