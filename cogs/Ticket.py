import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import aiosqlite
import os
import asyncio
import ezcord
import logging
import json
from source.paths import get_tickets_db_path
from source.settings import settings

logger = logging.getLogger('discord_bot')

# Konstanten
DB_PATH = get_tickets_db_path()
DB_FOLDER = os.path.dirname(DB_PATH)


async def _load_config_from_db(guild_id: int):
    """Lade die Ticket-Konfiguration aus der Datenbank"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''
                SELECT allowed_roles FROM ticket_config WHERE guild_id = ?
            ''', (guild_id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    return json.loads(result[0])  # allowed_roles ist JSON String
                return []
    except Exception as e:
        logger.error(f"Fehler beim Laden der Ticket-Config aus DB: {e}")
        return []


async def _save_config_to_db(guild_id: int, allowed_role_ids: list, role_names: list):
    """Speichere die Ticket-Konfiguration in der Datenbank"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            allowed_roles_json = json.dumps(allowed_role_ids)
            await db.execute('''
                INSERT OR REPLACE INTO ticket_config (guild_id, allowed_roles, role_names)
                VALUES (?, ?, ?)
            ''', (guild_id, allowed_roles_json, json.dumps(role_names)))
            await db.commit()
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Ticket-Config in DB: {e}")


class RoleSelectDropdown(Select):
    """Dropdown zur Auswahl von Rollen für Ticket-Zugriff"""
    
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        
        # Sammle alle Rollen (außer @everyone)
        options = [
            discord.SelectOption(
                label=role.name,
                value=str(role.id),
                emoji="👤"
            )
            for role in sorted(guild.roles, key=lambda r: r.position, reverse=True)
            if role.name != "@everyone" and not role.managed
        ]
        
        super().__init__(
            placeholder="Wähle Rollen die Tickets bearbeiten können...",
            min_values=1,
            max_values=min(len(options), 25) if options else 1,
            options=options[:25]  # Discord Limit: 25 Optionen
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Speichere die ausgewählten Rollen in der DB"""
        await interaction.response.defer()
        
        selected_role_ids = [int(role_id) for role_id in self.values]
        role_names = [self.guild.get_role(rid).name for rid in selected_role_ids if self.guild.get_role(rid)]
        
        # Speichere Config in DB
        await _save_config_to_db(self.guild.id, selected_role_ids, role_names)
        
        # Aktualisiere das Embed
        embed = discord.Embed(
            title="✅ Ticket-Rollen konfiguriert",
            description="Die folgenden Rollen können jetzt Tickets bearbeiten:",
            color=discord.Color.green()
        )
        
        role_text = "\n".join([
            f"• {self.guild.get_role(rid).mention}"
            for rid in selected_role_ids
            if self.guild.get_role(rid)
        ])
        embed.add_field(name="Berechtigte Rollen", value=role_text, inline=False)
        embed.add_field(
            name="🎫 Ticket Button",
            value="Jetzt kannst du einen Button mit `/setup_ticket_message` hinzufügen!",
            inline=False
        )
        
        await interaction.edit_original_response(embed=embed, view=None)
        logger.info(f"Ticket-Rollen für Guild {self.guild.id} konfiguriert")


class RoleSelectView(View):
    """View für die Rollen-Auswahl"""
    
    def __init__(self, bot, guild):
        super().__init__()
        self.add_item(RoleSelectDropdown(bot, guild))


class CreateTicketButton(Button):
    """Button zum Erstellen eines neuen Tickets"""
    def __init__(self, bot):
        super().__init__(
            style=discord.ButtonStyle.green,
            label="Create Ticket",
            emoji="🎫"
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        ticket_system = self.bot.get_cog('TicketSystem')
        await ticket_system.create_ticket(interaction)


class CloseTicketButton(Button):
    """Button zum Schließen eines Tickets"""
    def __init__(self, bot, guild_id: int, member_id: int):
        super().__init__(
            style=discord.ButtonStyle.red,
            label="Close Ticket",
            emoji="🔒"
        )
        self.bot = bot
        self.guild_id = guild_id
        self.member_id = member_id

    async def callback(self, interaction: discord.Interaction):
        ticket_system = self.bot.get_cog('TicketSystem')
        await ticket_system.close_ticket(interaction, self.guild_id, self.member_id)


class TicketView(View):
    """View mit Create-Ticket Button"""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(CreateTicketButton(bot))


class CloseTicketView(View):
    """View mit Close-Ticket Button"""
    def __init__(self, bot, guild_id: int, member_id: int):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton(bot, guild_id, member_id))


class TicketSystem(ezcord.Cog, emoji="🎫"):
    """
    Verwaltungssystem für Support-Tickets mit Rollen-Permissions.
    
    Funktionen:
    - Setup mit automatischer Kategorie-Erstellung
    - Rollen-basierte Permissions
    - Speicherung in Datenbank
    - Ticket-Verwaltung
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialisiert die Datenbank synchron."""
        if not os.path.exists(DB_FOLDER):
            os.makedirs(DB_FOLDER)
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS tickets
            (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS ticket_config
            (
                guild_id INTEGER PRIMARY KEY,
                allowed_roles TEXT NOT NULL,
                role_names TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Ticket-Datenbank initialisiert")

    async def add_ticket(self, guild_id: int, user_id: int, channel_id: int):
        """Speichert ein neues Ticket in der Datenbank."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO tickets (guild_id, user_id, channel_id)
                    VALUES (?, ?, ?)
                ''', (guild_id, user_id, channel_id))
                await db.commit()
                logger.info(f"Ticket erstellt: Guild {guild_id}, User {user_id}, Channel {channel_id}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Tickets: {e}")

    async def remove_ticket(self, guild_id: int, user_id: int):
        """Löscht ein Ticket aus der Datenbank."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    DELETE FROM tickets WHERE guild_id = ? AND user_id = ?
                ''', (guild_id, user_id))
                await db.commit()
                logger.info(f"Ticket gelöscht: Guild {guild_id}, User {user_id}")
        except Exception as e:
            logger.error(f"Fehler beim Löschen des Tickets: {e}")

    async def get_ticket(self, guild_id: int, user_id: int) -> int | None:
        """Ruft die Channel-ID eines Tickets ab."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT channel_id FROM tickets WHERE guild_id = ? AND user_id = ?
                ''', (guild_id, user_id)) as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else None
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Tickets: {e}")
            return None

    def _get_allowed_roles(self, guild_id: int) -> list:
        """Hole die erlaubten Rollen für einen Server aus der SQL-Konfiguration"""
        try:
            cfg = settings.get_config(guild_id)
            role_ids = cfg.get("ticket_role_ids", [])
            return [int(rid) if isinstance(rid, str) else rid for rid in role_ids]
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Ticket-Rollen: {e}")
            return []

    async def user_can_manage_tickets(self, member: discord.Member) -> bool:
        """Prüfe ob ein User Tickets bearbeiten darf"""
        if member.guild_permissions.administrator:
            return True
        
        allowed_role_ids = self._get_allowed_roles(member.guild.id)
        if not allowed_role_ids:
            return member.guild_permissions.manage_messages
        
        return any(role.id in allowed_role_ids for role in member.roles)

    # Hinweis: Setup-Befehle wurden entfernt und durch den zentralen `/setup`-Assistent ersetzt.
    # Ticket-Button kann über den Setup-Assistenten gepostet werden.

    async def create_ticket(self, interaction: discord.Interaction):
        """
        Erstellt einen neuen Ticket-Kanal für einen User.
        """
        guild = interaction.guild
        member = interaction.user
        
        # Bestätige die Interaction sofort (SEHR WICHTIG!)
        await interaction.response.defer(ephemeral=True)

        try:
            # Prüfe ob User bereits ein Ticket hat
            existing_channel_id = await self.get_ticket(guild.id, member.id)
            if existing_channel_id:
                existing_channel = guild.get_channel(existing_channel_id)
                if existing_channel:
                    await interaction.followup.send(
                        f"❌ Du hast bereits ein offenes Ticket: {existing_channel.mention}",
                        ephemeral=True
                    )
                    return
                else:
                    await self.remove_ticket(guild.id, member.id)

            # Hole Ticket-Kategorie oder erstelle sie
            cfg = settings.get_config(guild.id)
            category_id = cfg.get("ticket_category_id")
            category = None
            
            if category_id:
                category = guild.get_channel(int(category_id))
            
            if not category:
                # Fallback: Suche "🎫 Support Tickets" oder erstelle sie
                category = discord.utils.get(guild.categories, name="🎫 Support Tickets")
                if not category:
                    try:
                        category = await guild.create_category("🎫 Support Tickets")
                    except Exception as e:
                        logger.error(f"Fehler beim Erstellen der Ticket-Kategorie: {e}")
                        await interaction.followup.send(
                            "❌ Konnte Ticket-Kategorie nicht erstellen. Bitte Admin kontaktieren.",
                            ephemeral=True
                        )
                        return

            # Hole erlaubte Rollen
            allowed_role_ids = self._get_allowed_roles(guild.id)
            if not allowed_role_ids:
                await interaction.followup.send(
                    "❌ Keine Ticket-Rollen konfiguriert. Bitte Admin kontaktieren.",
                    ephemeral=True
                )
                return
            
            # Erstelle Channel mit Permissions
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            
            # Füge Supporter-Rollen hinzu
            for role_id in allowed_role_ids:
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        manage_messages=True
                    )

            channel = await guild.create_text_channel(
                f"ticket-{member.name}",
                overwrites=overwrites,
                category=category,
                topic=f"Support Ticket von {member.mention} | ID: {member.id}"
            )

            # Speichere Ticket in DB
            await self.add_ticket(guild.id, member.id, channel.id)

            # Sende Willkommens-Nachricht im Ticket
            embed = discord.Embed(
                title="🎫 Neues Support Ticket",
                description=f"Willkommen {member.mention}! Beschreibe bitte dein Anliegen. Das Support-Team wird sich gleich um dich kümmern.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="💡 Tipps",
                value="• Sei detailliert bei deinem Problem\n• Poste Screenshots wenn nötig\n• Warte geduldig auf eine Antwort",
                inline=False
            )
            
            view = CloseTicketView(self.bot, guild.id, member.id)
            await channel.send(embed=embed, view=view)
            
            # Benachrichtige den User
            await interaction.followup.send(
                f"✅ Dein Ticket wurde erstellt: {channel.mention}",
                ephemeral=True
            )
            logger.info(f"Ticket erstellt für {member.name} ({member.id}) auf {guild.name}")

        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Tickets: {e}")
            await interaction.followup.send(
                f"❌ Fehler beim Erstellen des Tickets: {e}",
                ephemeral=True
            )

    async def close_ticket(self, interaction: discord.Interaction, guild_id: int, member_id: int):
        """
        Schließt ein Ticket-Kanal und löscht ihn nach 2 Sekunden.
        WICHTIG: Interaction wird sofort bestätigt!
        """
        try:
            # Bestätige die Interaction sofort (SEHR WICHTIG!)
            await interaction.response.defer(ephemeral=True)
        except:
            pass  # Kann bereits bestätigt sein

        try:
            channel_id = await self.get_ticket(guild_id, member_id)
            if not channel_id:
                try:
                    await interaction.followup.send(
                        "❌ Dieses Ticket existiert nicht mehr.",
                        ephemeral=True
                    )
                except:
                    pass
                return

            channel = interaction.guild.get_channel(channel_id)

            # Sende Bestätigung ZUERST (bevor Channel gelöscht wird)
            try:
                await interaction.followup.send(
                    "✅ Ticket wird geschlossen und gelöscht.",
                    ephemeral=True
                )
            except Exception as e:
                logger.warning(f"Konnte Bestätigung nicht senden: {e}")

            # DANN mache lange Operationen
            if channel:
                # Sende Schließungs-Nachricht
                close_embed = discord.Embed(
                    title="🔒 Ticket wird geschlossen",
                    description="Dieser Kanal wird in 2 Sekunden gelöscht.",
                    color=discord.Color.red()
                )
                try:
                    await channel.send(embed=close_embed)
                except Exception as e:
                    logger.warning(f"Konnte Schließungs-Nachricht nicht senden: {e}")
                
                await asyncio.sleep(2)
                
                # Lösche Kanal
                try:
                    await channel.delete()
                except Exception as e:
                    logger.warning(f"Konnte Channel nicht löschen: {e}")

            # Lösche aus DB
            await self.remove_ticket(guild_id, member_id)

            # Benachrichtige User per DM
            try:
                user = await self.bot.fetch_user(member_id)
                dm_embed = discord.Embed(
                    title="✅ Ticket geschlossen",
                    description=f"Dein Support-Ticket auf {interaction.guild.name} wurde geschlossen.",
                    color=discord.Color.green()
                )
                await user.send(embed=dm_embed)
            except Exception as e:
                logger.warning(f"Konnte DM nicht senden an User {member_id}: {e}")

            logger.info(f"Ticket geschlossen von {interaction.user.name}")

        except Exception as e:
            logger.error(f"Fehler beim Schließen des Tickets: {e}")
            try:
                await interaction.followup.send(
                    f"❌ Fehler beim Schließen: {e}",
                    ephemeral=True
                )
            except:
                pass  # Kann nicht mehr senden


def setup(bot):
    """Lädt den Ticket System Cog."""
    bot.add_cog(TicketSystem(bot))


