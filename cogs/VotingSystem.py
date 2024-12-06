import discord
import ezcord
from discord.commands import slash_command
import requests

class PollDropdownView(discord.ui.View):
    def __init__(self, options):
        super().__init__()
        self.options = options
        self.add_item(self.create_select())

    def create_select(self):
        return discord.ui.Select(
            placeholder="Choose your Vote!",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=option) for option in self.options]
        )

    @discord.ui.select(
        placeholder="Choose your Vote!",
        min_values=1,
        max_values=1
    )
    async def select_callback(self, select, interaction):
        await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!")


class VotingSystem(ezcord.Cog, emoji="🗳️", group="Moderation"):
    @slash_command()
    async def poll(self, ctx, *options: str):
        if len(options) < 2:
            await ctx.send("Please provide at least two options for the poll.")
            return
        view = PollDropdownView(options=options)
        await ctx.respond("Please choose an option for the poll:", view=view)


''' 
TODO: Code Fixen funktioniert noch nicht der Fehler (TypeError: VotingSystem.poll() got an unexpected keyword argument 'options')
daher muss die options option zu mehreren einzelnen optionen oder zu einem array geändert werden denke ich :)
'''

def setup(bot):
    bot.add_cog(VotingSystem(bot))
