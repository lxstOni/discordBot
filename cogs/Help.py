"""
Help Command mit Dropdown-Menü für alle Commands.
Zeigt alle Commands übersichtlich gruppiert nach Kategorien.
"""

import discord
import ezcord
from discord.ext import commands


class HelpDropdown(discord.ui.Select):
    """
    Dropdown-Menü für die Auswahl von Command-Kategorien.
    """
    
    def __init__(self, bot):
        self.bot = bot
        
        # Definiere die Kategorien mit ihren Optionen
        options = [
            discord.SelectOption(
                label="👤 User Commands",
                value="user_commands",
                description="Benutzer- und Server-Informationen",
                emoji="👤"
            ),
            discord.SelectOption(
                label="🎫 Ticket System",
                value="ticket_system",
                description="Support Ticket System verwalten",
                emoji="🎫"
            ),
            discord.SelectOption(
                label="🕵️‍♂️ Moderation",
                value="moderation",
                description="Moderations-Commands: Ban, Kick, Clear",
                emoji="🕵️‍♂️"
            ),
            discord.SelectOption(
                label="📶 Level System",
                value="level_system",
                description="XP und Levels verdienen",
                emoji="📶"
            ),
            discord.SelectOption(
                label="🎮 Spiele",
                value="games",
                description="Spiele: Memes, Rock Paper Scissors",
                emoji="🎮"
            ),
            discord.SelectOption(
                label="👋 Welcome System",
                value="welcome",
                description="Willkommens-System für neue Member",
                emoji="👋"
            ),
            discord.SelectOption(
                label="🔛 Join to Create",
                value="join_to_create",
                description="Automatische Kanäle beim Beitreten",
                emoji="🔛"
            ),
            discord.SelectOption(
                label="🔑 Owner Commands",
                value="owner",
                description="Nur für den Bot Owner",
                emoji="🔑"
            ),
        ]
        
        super().__init__(
            placeholder="Wähle eine Kategorie...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        """Wird aufgerufen wenn eine Option gewählt wird."""
        
        # Mapping von Cog-Namen zu Kategorien
        cog_mapping = {
            "user_commands": "UserCmds",
            "ticket_system": "TicketSystem",
            "moderation": "Moderation",
            "level_system": "LevelSystem",
            "games": ["Memes", "RockPaperScissors"],
            "welcome": "Welcome",
            "join_to_create": "JoinToCreate",
            "owner": "OwnerCmds",
        }
        
        selected = self.values[0]
        cog_names = cog_mapping[selected]
        
        # Stelle sicher dass cog_names eine Liste ist
        if isinstance(cog_names, str):
            cog_names = [cog_names]
        
        # Sammle Commands aus den entsprechenden Cogs
        commands_list = []
        for cog_name in cog_names:
            cog = self.bot.get_cog(cog_name)
            if cog:
                for cmd in cog.get_commands():
                    # Prüfe ob Command versteckt ist (mit getattr sicher)
                    if not getattr(cmd, 'hidden', False):
                        commands_list.append(cmd)
        
        # Erstelle das Embed
        embed = discord.Embed(
            title=f"📚 {self.values[0].replace('_', ' ').title()}",
            description="Alle verfügbaren Commands in dieser Kategorie",
            color=discord.Color.blurple()
        )
        
        if commands_list:
            cmd_text = "\n".join([
                f"`/{cmd.name}` - {cmd.description or 'Keine Beschreibung'}"
                for cmd in commands_list
            ])
            embed.add_field(
                name="Commands",
                value=cmd_text,
                inline=False
            )
        else:
            embed.description = "Keine Commands in dieser Kategorie verfügbar."
        
        embed.set_footer(text="Wähle eine andere Kategorie aus dem Dropdown")
        
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    """
    View für den Help Command mit Dropdown.
    """
    
    def __init__(self, bot):
        super().__init__()
        self.add_item(HelpDropdown(bot))


class Help(ezcord.Cog, emoji="❓", description="Help Command - Alle Commands anschauen"):
    """
    Cog für den Help Command mit Dropdown-Menü.
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="help", description="Zeige alle verfügbaren Commands")
    async def help_command(self, ctx: discord.ApplicationContext):
        """
        Haupthilfe-Command mit Dropdown-Menü zur Auswahl von Kategorien.
        """
        
        embed = discord.Embed(
            title="🤖 Bot Help - Wähle eine Kategorie",
            description="Verwende das Dropdown-Menü unten um eine Command-Kategorie zu wählen.",
            color=discord.Color.blurple()
        )
        
        # Zähle die Commands pro Kategorie
        categories = {
            "👤 User Commands": "UserCmds",
            "🎫 Ticket System": "TicketSystem",
            "🕵️‍♂️ Moderation": "Moderation",
            "📶 Level System": "LevelSystem",
            "🎮 Spiele": ["Memes", "RockPaperScissors"],
            "👋 Welcome System": "Welcome",
            "🔛 Join to Create": "JoinToCreate",
            "🔑 Owner Commands": "OwnerCmds",
        }
        
        category_info = []
        for cat_name, cog_names in categories.items():
            if isinstance(cog_names, str):
                cog_names = [cog_names]
            
            cmd_count = 0
            for cog_name in cog_names:
                cog = self.bot.get_cog(cog_name)
                if cog:
                    cmd_count += len([c for c in cog.get_commands() if not getattr(c, 'hidden', False)])
            
            if cmd_count > 0:
                category_info.append(f"{cat_name}: {cmd_count} Commands")
        
        embed.add_field(
            name="📋 Kategorien",
            value="\n".join(category_info),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tipps",
            value="• Nutze das Dropdown-Menü um Commands einer Kategorie zu sehen\n"
                  "• Admin-Commands benötigen Administrator-Rechte\n"
                  "• Owner-Commands sind nur für den Bot Owner verfügbar",
            inline=False
        )
        
        embed.set_footer(text="Help Command mit Kategorie-Auswahl")
        
        view = HelpView(self.bot)
        await ctx.respond(embed=embed, view=view, ephemeral=True)


def setup(bot):
    """Lädt den Help Cog."""
    bot.add_cog(Help(bot))
