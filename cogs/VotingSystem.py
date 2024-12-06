import discord
import ezcord
from discord.commands import slash_command
import requests
from discord.ui import Select, View


class PollDropdownView(View):
    def __init__(self, options):
        super().__init__()
        self.options = options
        self.add_item(self.create_select())

    def create_select(self):
        return Select(
            placeholder="Choose your vote...",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=option) for option in self.options]
        )

    @discord.ui.select()
    async def poll_select(self, select: discord.ui.Select, interaction: discord.Interaction):
        selected_option = select.values[0]
        await interaction.response.send_message(f"Your vote for '{selected_option}' has been recorded!")




class VotingSystem(ezcord.Cog, emoji="🗳️",group="Moderation"):
    @slash_command()
    async def poll(ctx, *options: str):
        if len(options) < 2:
            await ctx.send("Please provide at least two options for the poll.")
            return
        view = PollDropdownView(options)
        await ctx.respond("Please choose an option for the poll:", view=view)



def setup(bot):
    bot.add_cog(VotingSystem(bot))