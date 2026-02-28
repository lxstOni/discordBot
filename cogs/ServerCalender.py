import discord
import sqlite3
from datetime import datetime, timedelta, timezone

import aiosqlite
import discord
import ezcord
from discord.commands import Option, slash_command
import pytz

from source.paths import get_config_db_path


BERLIN_TZ = pytz.timezone("Europe/Berlin")


class ServerCalender(ezcord.Cog, emoji="🗓️", description="Kalender-Events erstellen und verwalten"):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = get_config_db_path()
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                location TEXT,
                creator_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()

    @staticmethod
    def _parse_local_datetime(date_value: str, time_value: str) -> datetime:
        parsed = datetime.strptime(f"{date_value} {time_value}", "%d.%m.%Y %H:%M")
        localized = BERLIN_TZ.localize(parsed)
        return localized.astimezone(timezone.utc)

    @staticmethod
    def _to_discord_timestamp(utc_iso: str) -> int:
        utc_dt = datetime.fromisoformat(utc_iso)
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)
        return int(utc_dt.timestamp())

    @staticmethod
    def _build_event_embed(title: str, event_row: dict, color: discord.Color) -> discord.Embed:
        start_ts = ServerCalender._to_discord_timestamp(event_row["start_time"])
        end_ts = ServerCalender._to_discord_timestamp(event_row["end_time"])

        embed = discord.Embed(title=title, color=color)
        embed.add_field(name="Event-ID", value=str(event_row["id"]), inline=True)
        embed.add_field(name="Titel", value=event_row["title"], inline=True)
        embed.add_field(name="Ort", value=event_row["location"] or "Nicht gesetzt", inline=True)
        embed.add_field(name="Start", value=f"<t:{start_ts}:F> (<t:{start_ts}:R>)", inline=False)
        embed.add_field(name="Ende", value=f"<t:{end_ts}:F>", inline=False)
        embed.add_field(
            name="Beschreibung",
            value=event_row["description"] or "Keine Beschreibung",
            inline=False,
        )
        return embed

    async def _fetch_event(self, guild_id: int, event_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT id, guild_id, title, description, start_time, end_time, location, creator_id
                FROM calendar_events
                WHERE guild_id = ? AND id = ?
                """,
                (guild_id, event_id),
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    @staticmethod
    def _can_manage_calendar(member: discord.Member) -> bool:
        perms = member.guild_permissions
        return perms.administrator or perms.manage_events or perms.manage_guild

    @slash_command(name="event_erstellen", description="Erstelle ein neues Kalender-Event")
    async def event_erstellen(
        self,
        ctx: discord.ApplicationContext,
        titel: Option(str, "Titel des Events"),
        datum: Option(str, "Datum im Format TT.MM.JJJJ"),
        uhrzeit: Option(str, "Uhrzeit im Format HH:MM (24h)"),
        dauer_minuten: Option(int, "Dauer in Minuten", min_value=5, max_value=10080),
        beschreibung: Option(str, "Optionale Beschreibung", required=False, default=""),
        ort: Option(str, "Optionale Location", required=False, default=""),
    ):
        if not self._can_manage_calendar(ctx.author):
            await ctx.respond(
                "❌ Du brauchst `Events verwalten` (oder Admin), um Kalender-Einträge zu erstellen.",
                ephemeral=True,
            )
            return

        try:
            start_utc = self._parse_local_datetime(datum, uhrzeit)
        except ValueError:
            await ctx.respond(
                "❌ Ungültiges Datum/Uhrzeit-Format. Nutze `TT.MM.JJJJ` und `HH:MM`.",
                ephemeral=True,
            )
            return

        if start_utc <= datetime.now(timezone.utc):
            await ctx.respond("❌ Der Startzeitpunkt muss in der Zukunft liegen.", ephemeral=True)
            return

        end_utc = start_utc + timedelta(minutes=dauer_minuten)

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO calendar_events (guild_id, title, description, start_time, end_time, location, creator_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ctx.guild.id,
                    titel.strip(),
                    beschreibung.strip(),
                    start_utc.isoformat(),
                    end_utc.isoformat(),
                    ort.strip(),
                    ctx.author.id,
                ),
            )
            await db.commit()
            event_id = cursor.lastrowid

        created_event = await self._fetch_event(ctx.guild.id, event_id)
        embed = self._build_event_embed("✅ Event erstellt", created_event, discord.Color.green())
        await ctx.respond(embed=embed)

    @slash_command(name="event_liste", description="Zeigt eine Übersicht kommender Events")
    async def event_liste(
        self,
        ctx: discord.ApplicationContext,
        limit: Option(int, "Wie viele Events sollen angezeigt werden?", required=False, default=10, min_value=1, max_value=25),
    ):
        now_iso = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT id, title, start_time, end_time, location
                FROM calendar_events
                WHERE guild_id = ? AND start_time >= ?
                ORDER BY start_time ASC
                LIMIT ?
                """,
                (ctx.guild.id, now_iso, limit),
            ) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await ctx.respond("📭 Es sind keine kommenden Events vorhanden.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🗓️ Kommende Events",
            description="Nutze `event_bearbeiten` oder `event_loeschen` mit der Event-ID.",
            color=discord.Color.blurple(),
        )

        for row in rows:
            item = dict(row)
            start_ts = self._to_discord_timestamp(item["start_time"])
            end_ts = self._to_discord_timestamp(item["end_time"])
            location = item["location"] or "Nicht gesetzt"
            embed.add_field(
                name=f"#{item['id']} · {item['title']}",
                value=f"📍 {location}\n🕒 <t:{start_ts}:F> - <t:{end_ts}:t>",
                inline=False,
            )

        await ctx.respond(embed=embed)

    @slash_command(name="event_loeschen", description="Löscht ein Event anhand der Event-ID")
    async def event_loeschen(
        self,
        ctx: discord.ApplicationContext,
        event_id: Option(int, "Die Event-ID aus der Event-Liste"),
    ):
        if not self._can_manage_calendar(ctx.author):
            await ctx.respond(
                "❌ Du brauchst `Events verwalten` (oder Admin), um Kalender-Einträge zu löschen.",
                ephemeral=True,
            )
            return

        existing = await self._fetch_event(ctx.guild.id, event_id)
        if not existing:
            await ctx.respond("❌ Event nicht gefunden.", ephemeral=True)
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM calendar_events WHERE guild_id = ? AND id = ?",
                (ctx.guild.id, event_id),
            )
            await db.commit()

        await ctx.respond(f"🗑️ Event `#{event_id}` wurde gelöscht.", ephemeral=True)

    @slash_command(name="event_bearbeiten", description="Bearbeite ein bestehendes Event")
    async def event_bearbeiten(
        self,
        ctx: discord.ApplicationContext,
        event_id: Option(int, "Die Event-ID aus der Event-Liste"),
        titel: Option(str, "Neuer Titel", required=False, default=None),
        datum: Option(str, "Neues Datum (TT.MM.JJJJ)", required=False, default=None),
        uhrzeit: Option(str, "Neue Uhrzeit (HH:MM)", required=False, default=None),
        dauer_minuten: Option(int, "Neue Dauer in Minuten", required=False, default=None, min_value=5, max_value=10080),
        beschreibung: Option(str, "Neue Beschreibung", required=False, default=None),
        ort: Option(str, "Neue Location", required=False, default=None),
    ):
        if not self._can_manage_calendar(ctx.author):
            await ctx.respond(
                "❌ Du brauchst `Events verwalten` (oder Admin), um Kalender-Einträge zu bearbeiten.",
                ephemeral=True,
            )
            return

        event_data = await self._fetch_event(ctx.guild.id, event_id)
        if not event_data:
            await ctx.respond("❌ Event nicht gefunden.", ephemeral=True)
            return

        old_start = datetime.fromisoformat(event_data["start_time"])
        if old_start.tzinfo is None:
            old_start = old_start.replace(tzinfo=timezone.utc)
        old_start_local = old_start.astimezone(BERLIN_TZ)

        new_date = datum or old_start_local.strftime("%d.%m.%Y")
        new_time = uhrzeit or old_start_local.strftime("%H:%M")

        try:
            new_start_utc = self._parse_local_datetime(new_date, new_time)
        except ValueError:
            await ctx.respond(
                "❌ Ungültiges Datum/Uhrzeit-Format. Nutze `TT.MM.JJJJ` und `HH:MM`.",
                ephemeral=True,
            )
            return

        old_end = datetime.fromisoformat(event_data["end_time"])
        if old_end.tzinfo is None:
            old_end = old_end.replace(tzinfo=timezone.utc)
        old_duration = int((old_end - old_start).total_seconds() // 60)
        final_duration = dauer_minuten if dauer_minuten is not None else old_duration

        if new_start_utc <= datetime.now(timezone.utc):
            await ctx.respond("❌ Der Startzeitpunkt muss in der Zukunft liegen.", ephemeral=True)
            return

        new_end_utc = new_start_utc + timedelta(minutes=final_duration)
        final_title = titel.strip() if titel is not None else event_data["title"]
        final_description = beschreibung.strip() if beschreibung is not None else event_data["description"]
        final_location = ort.strip() if ort is not None else event_data["location"]

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE calendar_events
                SET title = ?, description = ?, start_time = ?, end_time = ?, location = ?, updated_at = CURRENT_TIMESTAMP
                WHERE guild_id = ? AND id = ?
                """,
                (
                    final_title,
                    final_description,
                    new_start_utc.isoformat(),
                    new_end_utc.isoformat(),
                    final_location,
                    ctx.guild.id,
                    event_id,
                ),
            )
            await db.commit()

        updated_event = await self._fetch_event(ctx.guild.id, event_id)
        embed = self._build_event_embed("✏️ Event bearbeitet", updated_event, discord.Color.orange())
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(ServerCalender(bot))