# 🤖 Discord Bot - Verwaltungs- & Unterhaltungssystem

Ein vollständig modulares Discord Bot-System mit erweiterten Features für Serververwaltung, Ticketsystem, Levelingsystem, Spiele und mehr.

**Image:** [`lxstoni/discordbot`](https://hub.docker.com/r/lxstoni/discordbot) auf Docker Hub

---

## ⚡ Quickstart

<details open>
<summary><b>🐳 Docker (empfohlen)</b></summary>

```bash
git clone <repository-url>
cd discordBot
echo "TOKEN=your_token_here" > .env
docker-compose -f Docker/docker-compose.yml up -d
```

</details>

<details>
<summary><b>🐍 Native (Python 3.12+)</b></summary>

```bash
git clone <repository-url>
cd discordBot
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "TOKEN=your_token_here" > .env
python main.py
```

</details>

---

## ✨ Features

| Feature | Beschreibung |
|---------|-------------|
| 🎫 **Tickets** | Rollbasiert, automatisch kategorisiert, datenbankgestützt |
| 📊 **Levels** | XP-System, `/rank` Befehl, Persistente Daten |
| ⚔️ **Moderation** | `/ban`, `/kick`, `/clear`, `/unban` |
| 🎮 **Spiele** | Rock-Paper-Scissors, Memes |
| 👋 **Welcome** | Personalisierte Willkommensnachrichten mit Bildern |
| 🔛 **Auto Channels** | Temporäre Voice-Kanäle |
| 📚 **Help** | Dynamisches Hilfe-System mit Dropdown |

---

## 🛠 Technologie

| Stack | Details |
|-------|---------|
| **Language** | Python 3.12 |
| **Bot Framework** | discord.py 2.6.0 + ezcord 0.6.4 |
| **Database** | SQLite (aiosqlite) |
| **Container** | Docker + Docker Compose |

---

## 📥 Detaillierte Installation

### 🐳 Docker Setup

**Für schnelles Deployment ohne Build-Prozess:**

```bash
# 1. Repository klonen
git clone <repository-url>
cd discordBot

# 2. Discord Token in .env eintragen
echo "TOKEN=your_discord_token_here" > .env

# 3. Starten
docker-compose -f Docker/docker-compose.yml up -d

# Logs: docker-compose -f Docker/docker-compose.yml logs -f
# Stop:  docker-compose -f Docker/docker-compose.yml down
```

**Eigenes Image bauen (optional, wenn du Code änderst):**

```bash
# Wichtig: Build-Kontext ist das Projekt-Root (Punkt), nicht der Docker/ Ordner
docker build -f Docker/Dockerfile -t discordbot:latest .
```

**Vollständige Anleitung:** Siehe [Docker/README.md](Docker/README.md)

---

### 🐍 Native Installation

#### Voraussetzungen
- Python 3.12+
- pip / venv
- [Discord Bot Token](#discord-token-erstellen)

#### Installation (6 Schritte)

```bash
# 1. Repository klonen
git clone <repository-url>
cd discordBot

# 2. Virtual Environment
python3.12 -m venv venv
source venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Token konfigurieren
echo "TOKEN=your_discord_bot_token_here" > .env

# 5. Bot starten
python main.py

# 6. In Discord Logs überprüfen: "Bot is ready!"
```

---

## 🔐 Discord Token erstellen

1. Gehe zu [Discord Developers](https://discord.com/developers/applications)
2. Klicke **"New Application"**
3. Unter **"Bot"** → **"Add Bot"**
4. Kopiere den Token → in `.env` eintragen
5. Intents aktivieren:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
   - ✅ Presence Intent
6. OAuth2 → URL Generator:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Administrator` (oder spezifische: Manage Channels, Ban, Kick, etc.)

---

## ⚙️ Konfiguration

### Bot-Token (.env)
```env
TOKEN=your_token_here
```

### Ticketsystem im Discord
```
/setup_ticket           # Kategorie & Rollen konfigurieren
/setup_ticket_message   # Ticket-Button posten
```

### Logging
- **Pfad:** `logs/bot.log`
- **Größe:** 5MB pro Datei (5 Backups)
- **Format:** Timestamp, Level, Message

---

## 🎮 Verfügbare Befehle

```
/help                   # Alle Befehle mit Kategorien
/rank [@user]          # Zeige Level & XP
/userinfo [@user]      # Benutzerinformationen
/serverinfo            # Server-Details
/ban @user [reason]    # Benutzer sperren
/kick @user [reason]   # Benutzer entfernen
/clear [count]         # Nachrichten löschen
/unban @user           # Entsperren
/rps [rock|paper|scissors]  # Spiel
/memes                 # Zufälliges Meme
```

---

## 📂 Projektstruktur

```
discordBot/
├── main.py                 # Bot-Einstiegspunkt
├── requirements.txt        # Dependencies
├── README.md              # Diese Datei
├── Docker/                # 🐳 Docker-Setup
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   └── README.md
├── cogs/                  # Bot-Module
│   ├── Ticket.py
│   ├── LevelSystem.py
│   ├── Moderation.py
│   ├── Welcome.py
│   ├── Help.py
│   └── ... (7 weitere)
├── source/                # Utilities
│   ├── paths.py          # Pfadverwaltung
│   ├── settings.py       # Logging
│   └── db/               # SQLite Datenbanken
└── logs/                 # Bot-Logs
```

---

## 🐛 Fehlerbehebung

<details>
<summary><b>Bot stellt keine Verbindung her</b></summary>

```bash
# 1. Token überprüfen
cat .env

# 2. Intents im Developer Portal aktivieren
# Message Content, Server Members, Presence

# 3. Bot auf Discord Server einladen (OAuth2 URL)
```

</details>

<details>
<summary><b>Permission denied Fehler</b></summary>

```bash
# 1. Bot-Rolle ist nicht oben genug in der Rollen-Hierarchie
# 2. Dem Bot diese Permissions geben:
#    - Manage Channels, Manage Roles, Ban, Kick, Manage Messages

# 3. In Discord: Server Settings → Roles → Bot nach oben verschieben
```

</details>

<details>
<summary><b>Docker Container startet nicht</b></summary>

```bash
# Logs anschauen
docker-compose -f Docker/docker-compose.yml logs

# Neubuild
docker-compose -f Docker/docker-compose.yml down -v
docker-compose -f Docker/docker-compose.yml up --build -d
```

</details>

<details>
<summary><b>Datenbank-Fehler</b></summary>

```bash
# Verzeichnis-Berechtigungen prüfen
ls -la source/db/

# Docker: Verzeichnisse neu erstellen
docker exec discord-bot mkdir -p /app/source/db /app/logs
```

</details>

---

## 📝 Häufig gestellte Fragen

**F: Kann ich neue Befehle hinzufügen?**  
A: Ja! Erstelle eine neue `.py` in `cogs/` mit `ezcord.Cog` - wird automatisch geladen.

**F: Funktioniert der Bot auf Windows/Mac?**  
A: Ja! Alle Pfade sind relativ und cross-platform kompatibel.

**F: Wie viel Speicherplatz?**  
A: ~200MB Dependencies + Logs. Datenbanken typisch <10MB.

**F: Bot auf mehreren Servern?**  
A: Ja! Eine Instanz kann beliebig viele Server verwalten.

---

## 🏗 Architektur-Highlights

- ✅ **Async/Await** - Nicht-blockierende Operationen
- ✅ **Cog-basiert** - Modulare, wartbare Struktur
- ✅ **Relative Pfade** - Cross-Platform kompatibel
- ✅ **Error Handling** - Try-Catch überall
- ✅ **Logging** - Rotating File Handler
- ✅ **Datenbank** - SQLite mit Async (aiosqlite)

---

## 🤝 Beiträge

1. Fork das Repository
2. Branch erstellen: `git checkout -b feature/Feature`
3. Committen: `git commit -m 'Add Feature'`
4. Push: `git push origin feature/Feature`
5. Pull Request erstellen

---

**Version:** 1.0  
**Python:** 3.12+  
**discord.py:** 2.6.0+  
**Status:** Production Ready ✅

