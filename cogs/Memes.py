import discord
import ezcord
from discord.commands import slash_command
import requests


class Memes(ezcord.Cog, emoji="🍪",description="Sending Random Memes",group="UserCmds"):
    @slash_command()
    async def memes(self, ctx:discord.ApplicationContext):
        r = requests.get("https://meme-api.com/gimme")
        res= r.json()
        em = discord.Embed()
        em.set_image(url=res['url'])
        await ctx.respond(embed=em)


def setup(bot):
    bot.add_cog(Memes(bot))