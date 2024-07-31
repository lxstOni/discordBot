import discord
import ezcord
from discord.commands import slash_command
import sqlite3
import asyncio
import datetime
import os


def setup_db():
    db_path = 'data/marriages.db'
    db_folder = os.path.dirname(db_path)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS marriages (
            user_id INTEGER PRIMARY KEY,
            partner_id INTEGER,
            marriage_date DATE
        )
    ''')
    conn.commit()
    conn.close()


class Marriage(ezcord.Cog, emoji="💍"):

    def set_marriage(self, user_id, partner_id):
        conn = sqlite3.connect('marriages.db')
        c = conn.cursor()
        c.execute("INSERT INTO marriages (user_id, partner_id, marriage_date) VALUES (?, ?, ?)", (user_id, partner_id, datetime.date.today()))
        conn.commit()
        conn.close()

    @slash_command()
    async def marry(self, ctx: discord.ApplicationContext, member: discord.Member):
        if member == ctx.author:
            await ctx.respond("You can't marry yourself!", ephemeral=True)
            return

        conn = sqlite3.connect('marriages.db')
        c = conn.cursor()
        c.execute("SELECT partner_id FROM marriages WHERE user_id = ?", (member.id,))
        result = c.fetchone()
        conn.close()

        if result:
            await ctx.respond(f"{member.display_name} is already married!", ephemeral=True)
            return

        conn = sqlite3.connect('marriages.db')
        c = conn.cursor()
        c.execute("SELECT partner_id FROM marriages WHERE user_id = ?", (ctx.author.id,))
        result = c.fetchone()
        conn.close()

        if result:
            await ctx.send("You are already married!")
            return

        propose_embed = discord.Embed(title="Marriage Proposal",
                                      description=f"{ctx.author.mention} has proposed to {member.mention}! "
                                                  f"Type `/accept_propose` to accept the proposal.",
                                      color=discord.Color.magenta())
        propose_embed.set_footer(text=f"Embed created from {ctx.bot.user.name}")
        await ctx.respond(embed=propose_embed)

        def check(m):
            return m.author == member and m.content == "/accept_propose"

        try:
            await ctx.bot.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send("Proposal timed out!")
        else:
            self.set_marriage(ctx.author.id, member.id)
            self.set_marriage(member.id, ctx.author.id)
            marriage_embed = discord.Embed(title="Marriage Confirmed",
                                           description=f"{ctx.author.mention} and {member.mention} are now married!",
                                           color=discord.Color.magenta())
            marriage_embed.set_footer(text=f"Embed created from {ctx.bot.user.name}")
            await ctx.send(embed=marriage_embed)


setup_db()


def setup(bot):
    bot.add_cog(Marriage(bot))
