import discord
import ezcord
from discord.commands import slash_command
class Userinfo(ezcord.Cog, emoji="👤"):
    @slash_command(description="Userinfo Infos")
    async def userinfo(self, ctx:discord.ApplicationContext, member: discord.Member):
        userinfo_embed = discord.Embed(title="Userinfo",
                                      description=f"Userinfo for {member.mention}",
                                      color=discord.Color.blurple())
        userinfo_embed.set_thumbnail(url=member.display_avatar)
        userinfo_embed.add_field(name="Username",value=f"{member.mention}", inline=True)
        userinfo_embed.add_field(name="Status", value=f"{member.status}")
        userinfo_embed.add_field(name="Bot:", value=f"{('Yes' if member.bot else 'No')}", inline=True)
        userinfo_embed.add_field(name="Created At", value=f"{member.created_at.strftime('%Y-%m-%d %H-%M-%S')}", inline=True)
        userinfo_embed.add_field(name="Joined At", value=f"{member.joined_at.strftime('%Y-%m-%d %H-%M-%S')}", inline=True)
        userinfo_embed.add_field(name="Roles", value=f"{len(member.roles) - 1}", inline=True)
        userinfo_embed.add_field(name="Highest Role", value=f"{member.top_role.mention}", inline=True)
        userinfo_embed.set_footer(text=f"Embed created from {ctx.bot.user.name}")

        await ctx.respond(embed=userinfo_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Userinfo(bot))