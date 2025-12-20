import discord
import ezcord
from discord.commands import slash_command, Option
import requests


class MyView(discord.ui.View):
    @discord.ui.select(
        placeholder = "RockPaperScissors",
        min_values = 1, 
        max_values = 1,
        options = [
            discord.SelectOption(
                label="Rock",
                description="Rock beats scissors!"
            ),
            discord.SelectOption(
                label="Paper",
                description="Paper beats stone!"
            ),
            discord.SelectOption(
                label="Scissors",
                description="Scissors beat paper!"
            )
        ]
    )
    async def select_callback(self, select, interaction):
        await interaction.response.send_message(f"{interaction.user} has picked **{select.values[0]}** !")


class RockPaperScissors(ezcord.Cog, emoji="✋", description="Stein Papier Schere Spiel"):
    @slash_command(description="Play Rock Paper Scissors with friends")
    async def rps(self,ctx:discord.ApplicationContext):
        await ctx.respond("Please Rock,Paper or Scissors",view=MyView())


def setup(bot):
    bot.add_cog(RockPaperScissors(bot))