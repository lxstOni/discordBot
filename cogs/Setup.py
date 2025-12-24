import discord
import ezcord
from discord.ext import commands

from source.settings import settings
from cogs.Ticket import TicketView


class Step1View(discord.ui.View):
    """Step 1: Rollen auswählen"""
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=600)
        self.guild = guild
        self.mod_role_ids: list[str] = []
        self.ticket_role_ids: list[str] = []

        # Mod-Rollen Select
        role_opts = [
            discord.SelectOption(label=r.name, value=str(r.id))
            for r in sorted(guild.roles, key=lambda r: r.position, reverse=True)
            if r.name != "@everyone" and not r.managed
        ][:25]
        self.mod_select = discord.ui.Select(
            placeholder="Mod-Rollen", min_values=0, max_values=min(len(role_opts), 25) if role_opts else 1,
            options=role_opts or [discord.SelectOption(label="Keine", value="none")]
        )
        self.mod_select.callback = self.mod_callback
        self.add_item(self.mod_select)

        # Ticket-Rollen Select
        self.ticket_select = discord.ui.Select(
            placeholder="Ticket-Rollen", min_values=0, max_values=min(len(role_opts), 25) if role_opts else 1,
            options=role_opts or [discord.SelectOption(label="Keine", value="none")]
        )
        self.ticket_select.callback = self.ticket_callback
        self.add_item(self.ticket_select)

        # Next Button
        next_btn = discord.ui.Button(label="Weiter →", style=discord.ButtonStyle.blurple)
        next_btn.callback = self.next_button
        self.add_item(next_btn)

    async def mod_callback(self, interaction: discord.Interaction):
        self.mod_role_ids = [v for v in self.mod_select.values if v != "none"]
        await interaction.response.defer()

    async def ticket_callback(self, interaction: discord.Interaction):
        self.ticket_role_ids = [v for v in self.ticket_select.values if v != "none"]
        await interaction.response.defer()

    async def next_button(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Nur Administratoren.", ephemeral=True)
        view = Step2View(self.guild, mod_ids=self.mod_role_ids, ticket_ids=self.ticket_role_ids)
        embed = discord.Embed(title="Bot Setup - Schritt 2/4: Kanäle (Allgemein)", color=discord.Color.blurple())
        embed.description = "Wähle Kanäle für Welcome und Join-to-Create."
        await interaction.response.edit_message(embed=embed, view=view)


class Step2View(discord.ui.View):
    """Step 2: Kanäle auswählen"""
    def __init__(self, guild: discord.Guild, mod_ids: list[str], ticket_ids: list[str]):
        super().__init__(timeout=600)
        self.guild = guild
        self.mod_role_ids = mod_ids
        self.ticket_role_ids = ticket_ids
        self.welcome_channel_id: str | None = None
        self.j2c_lobby_channel_id: str | None = None
        self.j2c_category_channel_id: str | None = None

        # Welcome Channel (Text)
        text_opts = [
            discord.SelectOption(label=ch.name, value=str(ch.id))
            for ch in guild.text_channels
        ][:25]
        self.welcome_select = discord.ui.Select(
            placeholder="Welcome-Channel", min_values=0, max_values=1,
            options=text_opts or [discord.SelectOption(label="Keine", value="none")]
        )
        self.welcome_select.callback = self.welcome_callback
        self.add_item(self.welcome_select)

        # J2C Lobby (Voice)
        voice_opts = [
            discord.SelectOption(label=ch.name, value=str(ch.id))
            for ch in guild.voice_channels
        ][:25]
        self.j2c_lobby_select = discord.ui.Select(
            placeholder="J2C Lobby (Voice)", min_values=0, max_values=1,
            options=voice_opts or [discord.SelectOption(label="Keine", value="none")]
        )
        self.j2c_lobby_select.callback = self.lobby_callback
        self.add_item(self.j2c_lobby_select)

        # J2C Category Trigger (Voice)
        self.j2c_category_select = discord.ui.Select(
            placeholder="J2C Kategorie-Trigger (Voice)", min_values=0, max_values=1,
            options=voice_opts or [discord.SelectOption(label="Keine", value="none")]
        )
        self.j2c_category_select.callback = self.category_callback
        self.add_item(self.j2c_category_select)

        # Back Button
        back_btn = discord.ui.Button(label="← Zurück", style=discord.ButtonStyle.secondary)
        back_btn.callback = self.back_button
        self.add_item(back_btn)

        # Next Button
        next_btn = discord.ui.Button(label="Weiter →", style=discord.ButtonStyle.blurple)
        next_btn.callback = self.next_button
        self.add_item(next_btn)

    async def welcome_callback(self, interaction: discord.Interaction):
        val = self.welcome_select.values[0] if self.welcome_select.values else None
        self.welcome_channel_id = None if (val == "none") else val
        await interaction.response.defer()

    async def lobby_callback(self, interaction: discord.Interaction):
        val = self.j2c_lobby_select.values[0] if self.j2c_lobby_select.values else None
        self.j2c_lobby_channel_id = None if (val == "none") else val
        await interaction.response.defer()

    async def category_callback(self, interaction: discord.Interaction):
        val = self.j2c_category_select.values[0] if self.j2c_category_select.values else None
        self.j2c_category_channel_id = None if (val == "none") else val
        await interaction.response.defer()

    async def back_button(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Nur Administratoren.", ephemeral=True)
        view = Step1View(self.guild)
        embed = discord.Embed(title="Bot Setup - Schritt 1/4: Rollen", color=discord.Color.blurple())
        embed.description = "Wähle Rollen für Moderation und Tickets aus."
        await interaction.response.edit_message(embed=embed, view=view)

    async def next_button(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Nur Administratoren.", ephemeral=True)
        view = Step3View(
            self.guild,
            mod_ids=self.mod_role_ids,
            ticket_ids=self.ticket_role_ids,
            welcome_ch=self.welcome_channel_id,
            j2c_lobby=self.j2c_lobby_channel_id,
            j2c_cat=self.j2c_category_channel_id,
        )
        embed = discord.Embed(title="Bot Setup - Schritt 3/4: Tickets", color=discord.Color.blurple())
        embed.description = "Wähle Channel für Ticket Embed und Ticket-Kategorie."
        await interaction.response.edit_message(embed=embed, view=view)


class Step3View(discord.ui.View):
    """Step 3: Ticket-Einstellungen (Channel und Kategorie)"""
    def __init__(
        self,
        guild: discord.Guild,
        mod_ids: list[str],
        ticket_ids: list[str],
        welcome_ch: str | None,
        j2c_lobby: str | None,
        j2c_cat: str | None,
    ):
        super().__init__(timeout=600)
        self.guild = guild
        self.mod_role_ids = mod_ids
        self.ticket_role_ids = ticket_ids
        self.welcome_channel_id = welcome_ch
        self.j2c_lobby_channel_id = j2c_lobby
        self.j2c_category_channel_id = j2c_cat
        self.ticket_embed_channel_id: str | None = None
        self.ticket_category_id: str | None = None

        # Ticket Embed Channel (Text)
        text_opts = [
            discord.SelectOption(label=ch.name, value=str(ch.id))
            for ch in guild.text_channels
        ][:25]
        self.embed_channel_select = discord.ui.Select(
            placeholder="Ticket Embed Channel (optional)", min_values=0, max_values=1,
            options=text_opts or [discord.SelectOption(label="Keine", value="none")]
        )
        self.embed_channel_select.callback = self.embed_channel_callback
        self.add_item(self.embed_channel_select)

        # Ticket Category (Category)
        cat_opts = [
            discord.SelectOption(label=cat.name, value=str(cat.id))
            for cat in guild.categories
        ][:25]
        self.category_select = discord.ui.Select(
            placeholder="Ticket-Kategorie (optional)", min_values=0, max_values=1,
            options=cat_opts or [discord.SelectOption(label="Keine", value="none")]
        )
        self.category_select.callback = self.category_callback
        self.add_item(self.category_select)

        # Back Button
        back_btn = discord.ui.Button(label="← Zurück", style=discord.ButtonStyle.secondary)
        back_btn.callback = self.back_button
        self.add_item(back_btn)

        # Next Button
        next_btn = discord.ui.Button(label="Weiter →", style=discord.ButtonStyle.blurple)
        next_btn.callback = self.next_button
        self.add_item(next_btn)

    async def embed_channel_callback(self, interaction: discord.Interaction):
        val = self.embed_channel_select.values[0] if self.embed_channel_select.values else None
        self.ticket_embed_channel_id = None if (val == "none") else val
        await interaction.response.defer()

    async def category_callback(self, interaction: discord.Interaction):
        val = self.category_select.values[0] if self.category_select.values else None
        self.ticket_category_id = None if (val == "none") else val
        await interaction.response.defer()

    async def back_button(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Nur Administratoren.", ephemeral=True)
        view = Step2View(self.guild, mod_ids=self.mod_role_ids, ticket_ids=self.ticket_role_ids)
        embed = discord.Embed(title="Bot Setup - Schritt 2/4: Kanäle (Allgemein)", color=discord.Color.blurple())
        embed.description = "Wähle Kanäle für Welcome und Join-to-Create."
        await interaction.response.edit_message(embed=embed, view=view)

    async def next_button(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Nur Administratoren.", ephemeral=True)
        view = Step4View(
            self.guild,
            mod_ids=self.mod_role_ids,
            ticket_ids=self.ticket_role_ids,
            welcome_ch=self.welcome_channel_id,
            j2c_lobby=self.j2c_lobby_channel_id,
            j2c_cat=self.j2c_category_channel_id,
            ticket_embed_ch=self.ticket_embed_channel_id,
            ticket_cat=self.ticket_category_id,
        )
        embed = discord.Embed(title="Bot Setup - Schritt 4/4: Speichern & Ticket-Button", color=discord.Color.blurple())
        embed.description = "Speichern oder Ticket-Button posten."
        await interaction.response.edit_message(embed=embed, view=view)


class Step4View(discord.ui.View):
    """Step 4: Speichern + Ticket-Button posten"""
    def __init__(
        self,
        guild: discord.Guild,
        mod_ids: list[str],
        ticket_ids: list[str],
        welcome_ch: str | None,
        j2c_lobby: str | None,
        j2c_cat: str | None,
        ticket_embed_ch: str | None,
        ticket_cat: str | None,
    ):
        super().__init__(timeout=600)
        self.guild = guild
        self.mod_role_ids = mod_ids
        self.ticket_role_ids = ticket_ids
        self.welcome_channel_id = welcome_ch
        self.j2c_lobby_channel_id = j2c_lobby
        self.j2c_category_channel_id = j2c_cat
        self.ticket_embed_channel_id = ticket_embed_ch
        self.ticket_category_id = ticket_cat

        # Back Button
        back_btn = discord.ui.Button(label="← Zurück", style=discord.ButtonStyle.secondary)
        back_btn.callback = self.back_button
        self.add_item(back_btn)

        # Save Button
        save_btn = discord.ui.Button(label="✅ Speichern", style=discord.ButtonStyle.green)
        save_btn.callback = self.save_button
        self.add_item(save_btn)

        # Post Ticket Button
        ticket_btn = discord.ui.Button(label="🎫 Ticket-Button posten", style=discord.ButtonStyle.blurple)
        ticket_btn.callback = self.post_ticket_button
        self.add_item(ticket_btn)

    async def back_button(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Nur Administratoren.", ephemeral=True)
        view = Step3View(
            self.guild,
            mod_ids=self.mod_role_ids,
            ticket_ids=self.ticket_role_ids,
            welcome_ch=self.welcome_channel_id,
            j2c_lobby=self.j2c_lobby_channel_id,
            j2c_cat=self.j2c_category_channel_id,
        )
        embed = discord.Embed(title="Bot Setup - Schritt 3/4: Tickets", color=discord.Color.blurple())
        embed.description = "Wähle Channel für Ticket Embed und Ticket-Kategorie."
        await interaction.response.edit_message(embed=embed, view=view)

    async def save_button(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Nur Administratoren.", ephemeral=True)
        updates = {
            "mod_role_ids": self.mod_role_ids,
            "ticket_role_ids": self.ticket_role_ids,
            "welcome_channel_id": self.welcome_channel_id,
            "j2c_lobby_channel_id": self.j2c_lobby_channel_id,
            "j2c_category_channel_id": self.j2c_category_channel_id,
            "ticket_embed_channel_id": self.ticket_embed_channel_id,
            "ticket_category_id": self.ticket_category_id,
        }
        settings.update_config(self.guild.id, updates)
        embed = discord.Embed(title="✅ Konfiguration gespeichert", color=discord.Color.green())
        def mention_role(rid: str):
            r = self.guild.get_role(int(rid)) if rid else None
            return r.mention if r else "—"
        def mention_channel(cid: str):
            ch = self.guild.get_channel(int(cid)) if cid else None
            return ch.mention if ch else "—"
        def mention_category(cid: str):
            cat = self.guild.get_channel(int(cid)) if cid else None
            return cat.mention if cat else "—"
        embed.add_field(name="Mod-Rollen", value=", ".join([mention_role(r) for r in self.mod_role_ids]) or "—", inline=False)
        embed.add_field(name="Ticket-Rollen", value=", ".join([mention_role(r) for r in self.ticket_role_ids]) or "—", inline=False)
        embed.add_field(name="Welcome-Channel", value=mention_channel(self.welcome_channel_id), inline=False)
        embed.add_field(name="J2C Lobby", value=mention_channel(self.j2c_lobby_channel_id), inline=True)
        embed.add_field(name="J2C Kategorie-Trigger", value=mention_channel(self.j2c_category_channel_id), inline=True)
        embed.add_field(name="Ticket Embed Channel", value=mention_channel(self.ticket_embed_channel_id) or "Standard", inline=False)
        embed.add_field(name="Ticket-Kategorie", value=mention_category(self.ticket_category_id) or "Standard (🎫 Support Tickets)", inline=False)
        await interaction.response.edit_message(embed=embed, view=None)

    async def post_ticket_button(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Nur Administratoren.", ephemeral=True)
        
        # Verwende den ausgewählten Ticket Embed Channel, oder den aktuellen Channel
        channel = None
        if self.ticket_embed_channel_id:
            channel = self.guild.get_channel(int(self.ticket_embed_channel_id))
        else:
            channel = interaction.channel
        
        if channel is None:
            return await interaction.response.send_message("Kein Kanal verfügbar.", ephemeral=True)
        
        embed = discord.Embed(
            title="🎫 Support Ticket erstellen",
            description="Klicke auf den Button unten, um ein neues Support-Ticket zu erstellen.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Was ist ein Ticket?",
            value="Ein privater Kanal nur für dich und dem Support-Team um dein Anliegen zu bearbeiten.",
            inline=False
        )
        embed.add_field(
            name="❓ Du brauchst Hilfe?",
            value="Erstelle einfach ein Ticket und warte auf eine Antwort vom Support-Team!",
            inline=False
        )
        await channel.send(embed=embed, view=TicketView(interaction.client))
        await interaction.response.send_message("✅ Ticket-Button gepostet.", ephemeral=True)


class Setup(ezcord.Cog, emoji="🛠", description="Server-Setup für Rollen & Kanäle"):
    def __init__(self, bot: ezcord.Bot):
        self.bot = bot
        settings.init_db()

    @commands.slash_command(name="setup", description="Einrichtungsassistent für den gesamten Bot")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx: discord.ApplicationContext):
        try:
            await ctx.defer(ephemeral=True)
            guild = ctx.guild
            if guild is None:
                return await ctx.respond("Nur in einem Server verfügbar.", ephemeral=True)

            embed = discord.Embed(title="Bot Setup - Schritt 1/4: Rollen", color=discord.Color.blurple())
            embed.description = "Wähle Rollen für Moderation und Tickets aus."
            await ctx.respond(embed=embed, view=Step1View(guild), ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Fehler: {e}", ephemeral=True)


def setup(bot: ezcord.Bot):
    bot.add_cog(Setup(bot))