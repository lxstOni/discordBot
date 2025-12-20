import discord
from discord.ext import commands
from discord.commands import slash_command
import ezcord
import aiosqlite
import random
import os


class LevelSystem(ezcord.Cog, emoji="📶", description="Level System - Verdiene XP und steige auf"):
    def __init__(self, bot):
        self.bot = bot
        self.DB = self.setup_db()

    def setup_db(self):
        db_path = 'source/db/level.db'
        db_folder = os.path.dirname(db_path)
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)
        return db_path

    @staticmethod
    def get_level(xp):
        lvl = 1
        amount = 100

        while True:
            xp -= amount
            if xp < 0:
                return lvl
            lvl += 1
            amount += 100

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                msg_count INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0
                )"""
            )
            await db.commit()

    async def check_user(self, user_id):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            await db.commit()

    async def get_xp(self, user_id):
        await self.check_user(user_id)
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
        return result[0]

    async def ensure_role(self, guild, role_name):
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            role = await guild.create_role(name=role_name, color=discord.Color.blue())
        return role

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return
        xp = random.randint(10, 20)

        await self.check_user(message.author.id)
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "UPDATE users SET msg_count = msg_count + 1, xp = xp + ? WHERE user_id = ?", (xp, message.author.id)
            )
            await db.commit()

        new_xp = await self.get_xp(message.author.id)

        old_level = self.get_level(new_xp - xp)
        new_level = self.get_level(new_xp)

        if old_level == new_level:
            return

        level_milestones = [2, 5, 10, 20]
        if new_level in level_milestones:
            role_name = f"Level {new_level}"
            role = await self.ensure_role(message.guild, role_name)
            await message.author.add_roles(role)
            await message.channel.send(f"Level Up! Du hast die Rolle {role.mention} erhalten!", ephemeral=True)

    @slash_command()
    async def rank(self, ctx):
        xp = await self.get_xp(ctx.author.id)
        lvl = self.get_level(xp)
        await ctx.respond(f"Du hast **{xp}** XP und bist Level **{lvl}**", ephemeral=True)

    @slash_command()
    async def leaderboard(self, ctx):
        desc = ""
        counter = 1
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute(
                    "SELECT user_id, xp FROM users WHERE msg_count > 0 ORDER BY xp DESC LIMIT 10"
            ) as cursor:
                async for user_id, xp in cursor:
                    desc += f"{counter}. <@{user_id}> - {xp} XP\n"
                    counter += 1

        embed = discord.Embed(
            title="Rangliste",
            description=desc,
            color=discord.Color.yellow()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(LevelSystem(bot))
