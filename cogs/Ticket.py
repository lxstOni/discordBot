import discord
from discord.ext import commands
from discord.ui import Button, View
import sqlite3
import os
import asyncio
import ezcord

def setup_db():
    db_path = 'source/db/tickets.db'
    db_folder = os.path.dirname(db_path)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets
        (guild_id INTEGER, user_id INTEGER, channel_id INTEGER,
        PRIMARY KEY (guild_id, user_id))
    ''')
    conn.commit()
    conn.close()


class CreateTicketButton(Button):
    def __init__(self, bot):
        super().__init__(style=discord.ButtonStyle.green, label="Create Ticket", emoji="🎫")
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        ticket_system = self.bot.get_cog('TicketSystem')
        await ticket_system.create_ticket(interaction)

class CloseTicketButton(Button):
    def __init__(self, bot, guild_id, member_id):
        super().__init__(style=discord.ButtonStyle.red, label="Close Ticket", emoji="🔒")
        self.bot = bot
        self.guild_id = guild_id
        self.member_id = member_id

    async def callback(self, interaction: discord.Interaction):
        ticket_system = self.bot.get_cog('TicketSystem')
        await ticket_system.close_ticket(interaction, self.guild_id, self.member_id)

class TicketView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.add_item(CreateTicketButton(bot))

class CloseTicketView(View):
    def __init__(self, bot, guild_id, member_id):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton(bot, guild_id, member_id))

class TicketSystem(ezcord.Cog, emoji="🎫"):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'data/tickets.db'


    def add_ticket(self, guild_id, user_id, channel_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO tickets (guild_id, user_id, channel_id)
            VALUES (?, ?, ?)
        ''', (guild_id, user_id, channel_id))
        conn.commit()
        conn.close()

    def remove_ticket(self, guild_id, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            DELETE FROM tickets WHERE guild_id = ? AND user_id = ?
        ''', (guild_id, user_id))
        conn.commit()
        conn.close()

    def get_ticket(self, guild_id, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT channel_id FROM tickets WHERE guild_id = ? AND user_id = ?
        ''', (guild_id, user_id))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    @commands.slash_command(name="setup_ticket", description="Sets up the ticket system")
    @commands.has_permissions(administrator=True)
    async def setup_ticket(self, ctx):
        embed = discord.Embed(
            title="Support Ticket",
            description="Click the button below to create a support ticket.",
            color=discord.Color.blue()
        )
        view = TicketView(self.bot)
        await ctx.respond(embed=embed, view=view)

    async def create_ticket(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user

        existing_channel_id = self.get_ticket(guild.id, member.id)
        if existing_channel_id:
            existing_channel = guild.get_channel(existing_channel_id)
            if existing_channel:
                await interaction.response.send_message(f"You already have an open ticket: {existing_channel.mention}",
                                                        ephemeral=True)
                return
            else:
                self.remove_ticket(guild.id, member.id)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        channel = await guild.create_text_channel(f"ticket-{member.name}", overwrites=overwrites,
                                                  category=interaction.channel.category)

        self.add_ticket(guild.id, member.id, channel.id)

        embed = discord.Embed(
            title="New Support Ticket",
            description=f"Welcome {member.mention}! Please describe your issue. A team member will assist you shortly.",
            color=discord.Color.green()
        )
        view = CloseTicketView(self.bot, guild.id, member.id)
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Your ticket has been created: {channel.mention}", ephemeral=True)

    async def close_ticket(self, interaction: discord.Interaction, guild_id, member_id):
        channel_id = self.get_ticket(guild_id, member_id)
        if not channel_id:
            await interaction.response.send_message("This ticket no longer exists.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(channel_id)

        if channel:
            await channel.send("This ticket will be closed in 2 seconds.")
            await asyncio.sleep(2)
            await channel.delete()

        self.remove_ticket(guild_id, member_id)

        user = await self.bot.fetch_user(member_id)
        await user.send(f"Your ticket on the server {interaction.guild.name} has been closed.")

# Set up the database
setup_db()

def setup(bot):
    bot.add_cog(TicketSystem(bot))


