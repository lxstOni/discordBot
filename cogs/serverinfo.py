import discord
import ezcord
from discord.commands import slash_command




class Serverinfo(ezcord.Cog, emoji="ℹ️"):
    @slash_command(description="Server Infos")
    async def serverinfo(self,ctx:discord.ApplicationContext):
        serverinfo_embed = discord.Embed(title="Serverinfo",
                                         description=f"Serverinfo for {ctx.guild.name}",
                                         color=discord.Color.green())
        serverinfo_embed.set_thumbnail(url=ctx.guild.icon)
        serverinfo_embed.add_field(name="Server Name", value=f"{ctx.guild.name}", inline=True)
        serverinfo_embed.add_field(name="Server ID", value=f"{ctx.guild.id}", inline=True)
        serverinfo_embed.add_field(name="Owner", value=f"{ctx.guild.owner}", inline=True)
        serverinfo_embed.add_field(name="Usercount", value=f"{ctx.guild.member_count}", inline=True)
        serverinfo_embed.add_field(name="Text Channels", value=f"{len(ctx.guild.text_channels)}",inline=True)
        serverinfo_embed.add_field(name="Voice Channels", value=f"{len(ctx.guild.voice_channels)}", inline=True)
        serverinfo_embed.add_field(name="Roles",value=f"{len(ctx.guild.roles)}", inline=True)
        serverinfo_embed.add_field(name="Boost Level", value=f"{ctx.guild.premium_tier}",inline=True)
        serverinfo_embed.add_field(name="Boost Count", value=f"{ctx.guild.premium_subscription_count}", inline=True)
        serverinfo_embed.add_field(name="Created At", value=f"{ctx.guild.created_at.strftime('%Y-%m-%d %H-%M-%S')}", inline=True)
        serverinfo_embed.set_footer(text=f"Embed created from {ctx.bot.user.name}")

        await ctx.respond(embed=serverinfo_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Serverinfo(bot))