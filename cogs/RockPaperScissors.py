import discord
import ezcord
from discord.commands import slash_command, Option
import requests


class MyView(discord.ui.View):
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "RockPaperScissors", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1,# the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
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


class RockPaperScissors(ezcord.Cog, emoji="✋",group="UserCmds"):
    @slash_command(description="Play Rock Paper Scissors with friends")
    async def rps(self,ctx:discord.ApplicationContext):
        await ctx.respond("Please Rock,Paper or Scissors",view=MyView())


def setup(bot):
    bot.add_cog(RockPaperScissors(bot))