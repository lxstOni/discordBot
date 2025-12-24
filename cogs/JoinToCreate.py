import discord
import ezcord
from discord.ext import commands
from source.settings import settings


class JoinToCreate(ezcord.Cog, emoji="🔛", description="Join to Create - Automatische Kanäle beim Beitreten"):

    def __init__(self, bot):
        self.bot = bot
        settings.init_db()

    @commands.Cog.listener()
    async def on_ready(self):
        # Cleanup: entferne leere temporäre Channels/Kategorien nach Restart
        for guild in self.bot.guilds:
            entries = settings.list_j2c_entries(guild.id)
            for e in entries:
                try:
                    if e["kind"] == "clone":
                        ch = guild.get_channel(int(e["channel_id"]))
                        if ch and isinstance(ch, discord.VoiceChannel) and len(ch.members) == 0:
                            await ch.delete(reason="J2C Cleanup: leer nach Restart")
                            settings.remove_j2c_entry(e["channel_id"])
                    elif e["kind"] == "category":
                        cat = guild.get_channel(int(e["category_id"]))
                        vc = guild.get_channel(int(e["voice_channel_id"])) if e["voice_channel_id"] else None
                        if cat and isinstance(cat, discord.CategoryChannel) and (vc is None or (isinstance(vc, discord.VoiceChannel) and len(vc.members) == 0)):
                            for ch in list(cat.channels):
                                try:
                                    await ch.delete(reason="J2C Cleanup: Kategorie leer nach Restart")
                                except Exception:
                                    pass
                            try:
                                await cat.delete(reason="J2C Cleanup")
                            except Exception:
                                pass
                            settings.remove_j2c_entry(e["category_id"])  # primary key
                except Exception:
                    continue

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        possible_channel_name = f"{member.display_name}'s area"
        
        if after.channel:
            cfg = settings.get_config(after.channel.guild.id)
            lobby_id = cfg.get("j2c_lobby_channel_id")
            category_trigger_id = cfg.get("j2c_category_channel_id")

            if lobby_id and str(after.channel.id) == str(lobby_id):
                temp_channel = await after.channel.clone(name=possible_channel_name)
                await member.move_to(temp_channel)
                settings.add_j2c_clone(after.channel.guild.id, temp_channel.id, temp_channel.name)

            elif category_trigger_id and str(after.channel.id) == str(category_trigger_id):
                temporary_category = await after.channel.guild.create_category(name=possible_channel_name)
                await temporary_category.create_text_channel(name="text")
                temp_channel = await temporary_category.create_voice_channel(name="voice")
                await member.move_to(temp_channel)
                settings.add_j2c_category(after.channel.guild.id, temporary_category.id, temp_channel.id, temporary_category.name)

        if before.channel:
            # Cleanup clone channels when empty
            entry = None
            for e in settings.list_j2c_entries(before.channel.guild.id):
                if str(e.get("channel_id")) == str(before.channel.id) and e.get("kind") == "clone":
                    entry = e
                    break
            if entry and len(before.channel.members) == 0:
                await before.channel.delete(reason="J2C: leer")
                settings.remove_j2c_entry(before.channel.id)

            # Cleanup category bundles when voice becomes empty
            cat_entry = None
            for e in settings.list_j2c_entries(before.channel.guild.id):
                if e.get("kind") == "category" and str(e.get("voice_channel_id")) == str(before.channel.id):
                    cat_entry = e
                    break
            if cat_entry and len(before.channel.members) == 0 and before.channel.category:
                for ch in list(before.channel.category.channels):
                    try:
                        await ch.delete(reason="J2C: Kategorie leer")
                    except Exception:
                        pass
                try:
                    await before.channel.category.delete(reason="J2C: Kategorie leer")
                except Exception:
                    pass
                settings.remove_j2c_entry(cat_entry.get("category_id"))

    def add_member_to_channel(self, channel_id, member_id):
        # optional: track members separately if needed; currently managed by Discord state
        return

    def remove_member_from_channel(self, channel_id, member_id):
        return

def setup(bot):
    bot.add_cog(JoinToCreate(bot))
