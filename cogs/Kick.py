import discord
from discord.commands import slash_command
import ezcord


class Kick(ezcord.Cog, emoji="💥"):
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



def setup(bot: discord.Bot):
    bot.add_cog(Kick(bot))