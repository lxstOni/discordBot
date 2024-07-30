import discord
import ezcord
from discord.commands import slash_command


class UserCmds(ezcord.Cog, emoji="🗣️", description="Standard Usercommands like Userinfo etc."):
    @slash_command(description="User Infos")
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
    bot.add_cog(UserCmds(bot))