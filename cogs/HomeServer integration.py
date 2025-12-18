"""
SSH Server Control für Discord Bot
Sichere Remote-Verwaltung von Servern über SSH mit moderner Discord UI
"""

import discord
from discord.ext import commands
from discord.ui import Select, View, Button
import paramiko
import asyncio
import os
import logging
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
import re

load_dotenv()

logger = logging.getLogger(__name__)


class ServerConfig:
    """Konfiguration für einen Server"""
    def __init__(self, name: str, host: str, user: str, key_path: str, port: int = 22, emoji: str = "🖥️"):
        self.name = name
        self.host = host
        self.user = user
        self.key_path = key_path
        self.port = port
        self.emoji = emoji


class SSHConnection:
    """SSH Verbindungs-Manager"""
    
    @staticmethod
    async def execute_command(
        server: ServerConfig,
        command: str,
        timeout: int = 30
    ) -> Tuple[bool, str, str]:
        """
        Führt einen Befehl über SSH aus
        
        Returns:
            (success: bool, stdout: str, stderr: str)
        """
        def _execute():
            try:
                # SSH Client erstellen
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Verbinden
                client.connect(
                    hostname=server.host,
                    port=server.port,
                    username=server.user,
                    key_filename=server.key_path,
                    timeout=10
                )
                
                # Befehl ausführen
                stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
                
                # Output lesen
                stdout_text = stdout.read().decode('utf-8', errors='replace')
                stderr_text = stderr.read().decode('utf-8', errors='replace')
                exit_code = stdout.channel.recv_exit_status()
                
                client.close()
                
                return (exit_code == 0, stdout_text, stderr_text)
                
            except paramiko.AuthenticationException:
                return (False, "", "SSH Authentifizierung fehlgeschlagen")
            except paramiko.SSHException as e:
                return (False, "", f"SSH Fehler: {str(e)}")
            except Exception as e:
                return (False, "", f"Fehler: {str(e)}")
        
        # In Thread ausführen um async nicht zu blockieren
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _execute)
    
    @staticmethod
    async def ping_server(server: ServerConfig, timeout: int = 5) -> bool:
        """Prüft ob Server erreichbar ist"""
        def _ping():
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    hostname=server.host,
                    port=server.port,
                    username=server.user,
                    key_filename=server.key_path,
                    timeout=timeout
                )
                client.close()
                return True
            except:
                return False
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _ping)


class ConfirmView(View):
    """Bestätigungs-Dialog mit Buttons"""
    
    def __init__(self, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.value = None
    
    @discord.ui.button(label="✅ Ja, ausführen", style=discord.ButtonStyle.danger)
    async def confirm(self, button: Button, interaction: discord.Interaction):
        self.value = True
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="❌ Abbrechen", style=discord.ButtonStyle.secondary)
    async def cancel(self, button: Button, interaction: discord.Interaction):
        self.value = False
        self.stop()
        await interaction.response.defer()


class ActionButtonsView(View):
    """Action Buttons nach Befehlsausführung"""
    
    def __init__(self, cog, server_name: str, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.server_name = server_name
    
    @discord.ui.button(label="📊 Status", style=discord.ButtonStyle.primary)
    async def status_button(self, button: Button, interaction: discord.Interaction):
        await interaction.response.defer()
        server = self.cog.servers.get(self.server_name)
        if server:
            await self.cog.show_server_status(interaction, server)
    
    @discord.ui.button(label="🔄 Ping", style=discord.ButtonStyle.secondary)
    async def ping_button(self, button: Button, interaction: discord.Interaction):
        await interaction.response.defer()
        server = self.cog.servers.get(self.server_name)
        if server:
            is_online = await SSHConnection.ping_server(server)
            status = "🟢 Online" if is_online else "🔴 Offline"
            await interaction.followup.send(f"{server.emoji} **{server.name}**: {status}", ephemeral=True)


class HomeServerIntegration(commands.Cog):
    """Server-Steuerung über SSH"""
    
    def __init__(self, bot):
        self.bot = bot
        self.servers: Dict[str, ServerConfig] = {}
        self.load_servers()
        
        # Command Log Channel
        self.log_channel_id = int(os.getenv("COMMAND_LOG_CHANNEL_ID", "0"))
        
        # Docker Compose Pfad
        self.docker_compose_path = os.getenv("DOCKER_COMPOSE_PATH", "/home/admin/docker")
        
        # Docker Projekte für Autocomplete
        self.docker_projects = os.getenv("DOCKER_PROJECTS", "").split(",")
        self.docker_projects = [p.strip() for p in self.docker_projects if p.strip()]
    
    def load_servers(self):
        """Lädt Server-Konfigurationen aus .env"""
        servers_list = os.getenv("SERVERS", "").split(",")
        
        for server_id in servers_list:
            server_id = server_id.strip()
            if not server_id:
                continue
            
            prefix = f"SERVER_{server_id.upper()}_"
            
            name = os.getenv(f"{prefix}NAME", server_id)
            host = os.getenv(f"{prefix}HOST")
            user = os.getenv(f"{prefix}USER")
            key_path = os.getenv(f"{prefix}KEY")
            port = int(os.getenv(f"{prefix}PORT", "22"))
            emoji = os.getenv(f"{prefix}EMOJI", "🖥️")
            
            if host and user and key_path:
                self.servers[server_id] = ServerConfig(name, host, user, key_path, port, emoji)
                logger.info(f"Server geladen: {name} ({host})")
            else:
                logger.warning(f"Unvollständige Konfiguration für Server: {server_id}")
    
    async def log_command(self, ctx: discord.ApplicationContext, server_name: str, command: str, success: bool):
        """Loggt Befehlsausführung"""
        if not self.log_channel_id:
            return
        
        channel = self.bot.get_channel(self.log_channel_id)
        if not channel:
            return
        
        embed = discord.Embed(
            title="📋 Server Command Log",
            color=discord.Color.green() if success else discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="User", value=f"{ctx.author.mention} ({ctx.author.id})", inline=False)
        embed.add_field(name="Server", value=server_name, inline=True)
        embed.add_field(name="Command", value=f"```{command}```", inline=False)
        embed.add_field(name="Status", value="✅ Erfolg" if success else "❌ Fehler", inline=True)
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Fehler beim Loggen: {e}")
    
    async def show_server_status(self, interaction: discord.Interaction, server: ServerConfig):
        """Zeigt umfassenden Server-Status"""
        embed = discord.Embed(
            title=f"{server.emoji} Server Status: {server.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Ping Check
        is_online = await SSHConnection.ping_server(server)
        status = "🟢 Online" if is_online else "🔴 Offline"
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Host", value=server.host, inline=True)
        embed.add_field(name="Port", value=str(server.port), inline=True)
        
        if is_online:
            # Uptime
            success, stdout, _ = await SSHConnection.execute_command(server, "uptime -p", timeout=10)
            if success:
                embed.add_field(name="⏱️ Uptime", value=stdout.strip(), inline=False)
            
            # Memory
            success, stdout, _ = await SSHConnection.execute_command(
                server, 
                "free -h | awk 'NR==2 {print $3\"/\"$2\" (\"$3/$2*100\"%)\"}'",
                timeout=10
            )
            if success:
                embed.add_field(name="🧠 Memory", value=stdout.strip(), inline=True)
            
            # Disk
            success, stdout, _ = await SSHConnection.execute_command(
                server,
                "df -h / | awk 'NR==2 {print $3\"/\"$2\" (\"$5\")\"}'",
                timeout=10
            )
            if success:
                embed.add_field(name="💾 Disk", value=stdout.strip(), inline=True)
            
            # CPU
            success, stdout, _ = await SSHConnection.execute_command(
                server,
                "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1",
                timeout=10
            )
            if success:
                cpu_usage = stdout.strip()
                embed.add_field(name="💻 CPU Usage", value=f"{cpu_usage}%", inline=True)
            
            # Docker Container (falls vorhanden)
            success, stdout, _ = await SSHConnection.execute_command(
                server,
                "docker ps --format '{{.Names}}' 2>/dev/null | wc -l",
                timeout=10
            )
            if success and stdout.strip().isdigit():
                container_count = stdout.strip()
                embed.add_field(name="🐳 Docker Container", value=container_count, inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @commands.slash_command(
        name="server_control",
        description="Steuert einen Server über SSH"
    )
    @commands.is_owner()
    async def server_control(
        self,
        ctx: discord.ApplicationContext,
        server: discord.Option(
            str,
            "Server auswählen",
            autocomplete=discord.utils.basic_autocomplete(lambda ctx: list(ctx.bot.get_cog("HomeServerIntegration").servers.keys()))
        ),
        command: discord.Option(
            str,
            "Befehl auswählen",
            choices=[
                "poweroff",
                "reboot",
                "status",
                "uptime",
                "disk_usage",
                "memory_usage",
                "docker_ps",
                "docker_stats"
            ]
        ),
        parameter: discord.Option(str, "Zusätzlicher Parameter (optional)", required=False, default="")
    ):
        """Führt einen Befehl auf dem Server aus"""
        await ctx.defer()
        
        # Server validieren
        if server not in self.servers:
            await ctx.respond("❌ Server nicht gefunden!", ephemeral=True)
            return
        
        server_config = self.servers[server]
        
        # Befehle definieren
        commands_map = {
            "poweroff": ("sudo poweroff", True),
            "reboot": ("sudo reboot", True),
            "status": ("echo 'Status wird abgerufen...'", False),  # Verwendet show_server_status
            "uptime": ("uptime -p", False),
            "disk_usage": ("df -h", False),
            "memory_usage": ("free -h", False),
            "docker_ps": ("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'", False),
            "docker_stats": ("docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'", False)
        }
        
        if command not in commands_map:
            await ctx.respond("❌ Unbekannter Befehl!", ephemeral=True)
            return
        
        cmd, requires_confirmation = commands_map[command]
        
        # Spezialfall: Status
        if command == "status":
            await self.show_server_status(ctx.interaction, server_config)
            return
        
        # Bestätigung für kritische Befehle
        if requires_confirmation:
            embed = discord.Embed(
                title="⚠️ Bestätigung erforderlich",
                description=f"**Server:** {server_config.emoji} {server_config.name}\n**Befehl:** `{cmd}`\n\nBist du sicher?",
                color=discord.Color.orange()
            )
            
            view = ConfirmView()
            await ctx.respond(embed=embed, view=view, ephemeral=True)
            await view.wait()
            
            if not view.value:
                await ctx.edit(content="❌ Abgebrochen", embed=None, view=None)
                return
            
            await ctx.edit(content=f"🔄 Führe Befehl aus...", embed=None, view=None)
        
        # Befehl ausführen
        success, stdout, stderr = await SSHConnection.execute_command(server_config, cmd, timeout=30)
        
        # Log
        await self.log_command(ctx, server_config.name, cmd, success)
        
        # Response
        if success:
            embed = discord.Embed(
                title=f"✅ Befehl erfolgreich ausgeführt",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Server", value=f"{server_config.emoji} {server_config.name}", inline=True)
            embed.add_field(name="Befehl", value=f"`{command}`", inline=True)
            
            if stdout and len(stdout.strip()) > 0:
                output = stdout[:1900]  # Discord Limit
                embed.add_field(name="Output", value=f"```\n{output}\n```", inline=False)
            
            # Monitoring für poweroff/reboot
            if command in ["poweroff", "reboot"]:
                embed.add_field(
                    name="🔍 Monitoring",
                    value="Server-Status wird überwacht...",
                    inline=False
                )
                
                view = ActionButtonsView(self, server)
                await ctx.respond(embed=embed, view=view)
                
                # Monitoring starten
                await self.monitor_server_shutdown(ctx, server_config, command)
            else:
                view = ActionButtonsView(self, server)
                await ctx.respond(embed=embed, view=view)
        else:
            embed = discord.Embed(
                title=f"❌ Befehl fehlgeschlagen",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Server", value=f"{server_config.emoji} {server_config.name}", inline=True)
            embed.add_field(name="Befehl", value=f"`{command}`", inline=True)
            
            if stderr:
                error = stderr[:1900]
                embed.add_field(name="Error", value=f"```\n{error}\n```", inline=False)
            
            await ctx.respond(embed=embed, ephemeral=True)
    
    async def monitor_server_shutdown(self, ctx, server: ServerConfig, action: str):
        """Überwacht Server nach poweroff/reboot"""
        await asyncio.sleep(10)  # Warte 10 Sekunden
        
        max_attempts = 6
        for attempt in range(max_attempts):
            await asyncio.sleep(5)
            is_online = await SSHConnection.ping_server(server, timeout=3)
            
            if not is_online:
                # Server ist offline
                embed = discord.Embed(
                    title=f"✅ Server '{server.name}' wurde {'heruntergefahren' if action == 'poweroff' else 'wird neu gestartet'}",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Status", value="🔴 Offline", inline=True)
                embed.add_field(name="Zeitpunkt", value=datetime.now().strftime("%H:%M:%S"), inline=True)
                
                try:
                    await ctx.followup.send(embed=embed)
                except:
                    pass
                
                # Bei Reboot weiter überwachen
                if action == "reboot":
                    await self.monitor_server_reboot(ctx, server)
                return
        
        # Timeout
        embed = discord.Embed(
            title="⚠️ Monitoring Timeout",
            description=f"Server '{server.name}' antwortet noch",
            color=discord.Color.orange()
        )
        try:
            await ctx.followup.send(embed=embed)
        except:
            pass
    
    async def monitor_server_reboot(self, ctx, server: ServerConfig):
        """Überwacht Server beim Neustart"""
        await asyncio.sleep(30)  # Warte 30 Sekunden
        
        max_attempts = 12  # 12 * 5 = 60 Sekunden
        for attempt in range(max_attempts):
            await asyncio.sleep(5)
            is_online = await SSHConnection.ping_server(server, timeout=3)
            
            if is_online:
                embed = discord.Embed(
                    title=f"✅ Server '{server.name}' ist wieder online",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Status", value="🟢 Online", inline=True)
                embed.add_field(name="Zeitpunkt", value=datetime.now().strftime("%H:%M:%S"), inline=True)
                
                try:
                    await ctx.followup.send(embed=embed)
                except:
                    pass
                return
        
        # Timeout
        embed = discord.Embed(
            title="⚠️ Server antwortet nicht",
            description=f"Server '{server.name}' ist nach Neustart nicht erreichbar",
            color=discord.Color.red()
        )
        try:
            await ctx.followup.send(embed=embed)
        except:
            pass
    
    @commands.slash_command(
        name="docker",
        description="Docker Compose Befehle ausführen"
    )
    @commands.is_owner()
    async def docker_compose(
        self,
        ctx: discord.ApplicationContext,
        server: discord.Option(
            str,
            "Server auswählen",
            autocomplete=discord.utils.basic_autocomplete(lambda ctx: list(ctx.bot.get_cog("HomeServerIntegration").servers.keys()))
        ),
        command: discord.Option(
            str,
            "Docker Compose Befehl",
            choices=["up", "down", "restart", "logs", "ps", "pull"]
        ),
        project: discord.Option(
            str,
            "Projekt-Name",
            autocomplete=discord.utils.basic_autocomplete(
                lambda ctx: ctx.bot.get_cog("HomeServerIntegration").docker_projects
            )
        ),
        options: discord.Option(str, "Zusätzliche Optionen (z.B. --build)", required=False, default="")
    ):
        """Führt Docker Compose Befehle aus"""
        await ctx.defer()
        
        if server not in self.servers:
            await ctx.respond("❌ Server nicht gefunden!", ephemeral=True)
            return
        
        server_config = self.servers[server]
        
        # Projekt-Pfad
        project_path = f"{self.docker_compose_path}/{project}"
        
        # Befehle zusammenbauen
        commands_map = {
            "up": f"cd {project_path} && docker compose up -d {options}",
            "down": f"cd {project_path} && docker compose down {options}",
            "restart": f"cd {project_path} && docker compose restart {options}",
            "logs": f"cd {project_path} && docker compose logs --tail=50 {options}",
            "ps": f"cd {project_path} && docker compose ps {options}",
            "pull": f"cd {project_path} && docker compose pull {options}"
        }
        
        cmd = commands_map.get(command)
        if not cmd:
            await ctx.respond("❌ Unbekannter Befehl!", ephemeral=True)
            return
        
        # Bestätigung für down
        if command == "down":
            embed = discord.Embed(
                title="⚠️ Docker Compose Down",
                description=f"**Server:** {server_config.emoji} {server_config.name}\n**Projekt:** {project}\n\nAlle Container stoppen?",
                color=discord.Color.orange()
            )
            
            view = ConfirmView()
            await ctx.respond(embed=embed, view=view, ephemeral=True)
            await view.wait()
            
            if not view.value:
                await ctx.edit(content="❌ Abgebrochen", embed=None, view=None)
                return
            
            await ctx.edit(content=f"🔄 Stoppe Container...", embed=None, view=None)
        
        # Status Message
        action_text = {
            "up": "🚀 Starte Container...",
            "down": "⏹️ Stoppe Container...",
            "restart": "🔄 Starte Container neu...",
            "logs": "📜 Lade Logs...",
            "ps": "📊 Lade Status...",
            "pull": "⬇️ Lade Images..."
        }
        
        status_msg = await ctx.respond(action_text.get(command, "🔄 Führe aus..."))
        
        # Befehl ausführen
        success, stdout, stderr = await SSHConnection.execute_command(server_config, cmd, timeout=120)
        
        # Log
        await self.log_command(ctx, server_config.name, f"docker compose {command} {project}", success)
        
        # Response
        if success:
            embed = discord.Embed(
                title=f"✅ Docker Compose {command.upper()} erfolgreich",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="📦 Projekt", value=project, inline=True)
            embed.add_field(name="🖥️ Server", value=f"{server_config.emoji} {server_config.name}", inline=True)
            
            if stdout and len(stdout.strip()) > 0:
                output = stdout[:1500]
                embed.add_field(name="Output", value=f"```\n{output}\n```", inline=False)
            
            # Container Status nach up/restart
            if command in ["up", "restart", "ps"]:
                ps_cmd = f"cd {project_path} && docker compose ps --format 'table {{{{.Name}}}}\t{{{{.Status}}}}'"
                ps_success, ps_stdout, _ = await SSHConnection.execute_command(server_config, ps_cmd, timeout=15)
                
                if ps_success and ps_stdout:
                    containers = ps_stdout[:1000]
                    embed.add_field(name="🐳 Container Status", value=f"```\n{containers}\n```", inline=False)
            
            view = ActionButtonsView(self, server)
            await ctx.edit(embed=embed, view=view)
        else:
            embed = discord.Embed(
                title=f"❌ Docker Compose {command.upper()} fehlgeschlagen",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="📦 Projekt", value=project, inline=True)
            embed.add_field(name="🖥️ Server", value=f"{server_config.emoji} {server_config.name}", inline=True)
            
            if stderr:
                error = stderr[:1500]
                embed.add_field(name="Error", value=f"```\n{error}\n```", inline=False)
            
            await ctx.edit(embed=embed)
    
    @commands.slash_command(
        name="server_status",
        description="Zeigt umfassenden Server-Status"
    )
    @commands.is_owner()
    async def server_status_cmd(
        self,
        ctx: discord.ApplicationContext,
        server: discord.Option(
            str,
            "Server auswählen",
            autocomplete=discord.utils.basic_autocomplete(lambda ctx: list(ctx.bot.get_cog("HomeServerIntegration").servers.keys()))
        )
    ):
        """Zeigt Server-Status"""
        await ctx.defer()
        
        if server not in self.servers:
            await ctx.respond("❌ Server nicht gefunden!", ephemeral=True)
            return
        
        server_config = self.servers[server]
        await self.show_server_status(ctx.interaction, server_config)
    
    @commands.slash_command(
        name="list_servers",
        description="Zeigt alle konfigurierten Server"
    )
    @commands.is_owner()
    async def list_servers(self, ctx: discord.ApplicationContext):
        """Listet alle Server auf"""
        await ctx.defer()
        
        if not self.servers:
            await ctx.respond("❌ Keine Server konfiguriert!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🖥️ Konfigurierte Server",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        for server_id, server in self.servers.items():
            # Ping server
            is_online = await SSHConnection.ping_server(server, timeout=3)
            status = "🟢 Online" if is_online else "🔴 Offline"
            
            embed.add_field(
                name=f"{server.emoji} {server.name}",
                value=f"**Host:** {server.host}\n**Status:** {status}",
                inline=True
            )
        
        await ctx.respond(embed=embed)
    
    @commands.slash_command(
        name="ping_server",
        description="Prüft ob ein Server erreichbar ist"
    )
    @commands.is_owner()
    async def ping_server_cmd(
        self,
        ctx: discord.ApplicationContext,
        server: discord.Option(
            str,
            "Server auswählen",
            autocomplete=discord.utils.basic_autocomplete(lambda ctx: list(ctx.bot.get_cog("HomeServerIntegration").servers.keys()))
        )
    ):
        """Pingt einen Server"""
        await ctx.defer()
        
        if server not in self.servers:
            await ctx.respond("❌ Server nicht gefunden!", ephemeral=True)
            return
        
        server_config = self.servers[server]
        
        embed = discord.Embed(
            title=f"🔍 Ping {server_config.name}",
            description="Prüfe Verbindung...",
            color=discord.Color.blue()
        )
        
        msg = await ctx.respond(embed=embed)
        
        is_online = await SSHConnection.ping_server(server_config, timeout=5)
        
        embed = discord.Embed(
            title=f"{server_config.emoji} {server_config.name}",
            color=discord.Color.green() if is_online else discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        status = "🟢 Online" if is_online else "🔴 Offline"
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Host", value=server_config.host, inline=True)
        embed.add_field(name="Port", value=str(server_config.port), inline=True)
        
        await ctx.edit(embed=embed)


def setup(bot):
    bot.add_cog(HomeServerIntegration(bot))
