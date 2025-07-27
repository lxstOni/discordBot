import discord
import ezcord
import json
from discord.ext import commands


temp_file_path = "/workspaces/discordBot/source/temporary_data.json"
class JoinToCreate(ezcord.Cog, emoji="🔛"):

    def __init__(self, bot):
        self.bot = bot
        self.load_data()

    def save_data(self):
        with open(temp_file_path, "w") as json_file:
            json.dump(self.temporary_data, json_file, indent=4)

    def load_data(self):
        try:
            with open(temp_file_path, "r") as json_file:
                self.temporary_data = json.load(json_file)
        except FileNotFoundError:
            self.temporary_data = {
                "temporary_channels": {},
                "temporary_categories": {}
            }

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        possible_channel_name = f"{member.display_name}'s area"
        
        if after.channel:
            if after.channel.name == "➕・Lobby":
                temp_channel = await after.channel.clone(name=possible_channel_name)
                await member.move_to(temp_channel)
                self.temporary_data["temporary_channels"][temp_channel.id] = {
                    "name": temp_channel.name,
                    "members": [member.id]
                }
                self.save_data()

            elif after.channel.name == 'area':
                temporary_category = await after.channel.guild.create_category(name=possible_channel_name)
                await temporary_category.create_text_channel(name="text")
                temp_channel = await temporary_category.create_voice_channel(name="voice")
                await member.move_to(temp_channel)
                self.temporary_data["temporary_categories"][temporary_category.id] = {
                    "name": temporary_category.name,
                    "voice_channel_id": temp_channel.id,
                    "members": [member.id]
                }
                self.save_data()

        if before.channel:
            if before.channel.id in self.temporary_data["temporary_channels"]:
                if len(before.channel.members) == 0:
                    del self.temporary_data["temporary_channels"][before.channel.id]
                    await before.channel.delete()
                    self.save_data()

            elif before.channel.id in self.temporary_data["temporary_categories"]:
                if len(before.channel.members) == 0:
                    for channel in before.channel.category.channels:
                        await channel.delete()
                    await before.channel.category.delete()
                    del self.temporary_data["temporary_categories"][before.channel.id]
                    self.save_data()

    def add_member_to_channel(self, channel_id, member_id):
        if channel_id in self.temporary_data["temporary_channels"]:
            self.temporary_data["temporary_channels"][channel_id]["members"].append(member_id)
            self.save_data()

    def remove_member_from_channel(self, channel_id, member_id):
        if channel_id in self.temporary_data["temporary_channels"]:
            if member_id in self.temporary_data["temporary_channels"][channel_id]["members"]:
                self.temporary_data["temporary_channels"][channel_id]["members"].remove(member_id)
                self.save_data()

def setup(bot):
    bot.add_cog(JoinToCreate(bot))
