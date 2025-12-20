# Docker Konfiguration

Das Discord Bot Image ist auf Docker Hub verfügbar: **[lxstOni/discord-bot](https://hub.docker.com/r/lxstOni/discord-bot)**

Alle Docker-bezogenen Dateien für einfaches Deployment.

## Dateien

- **Dockerfile** - Python 3.12 slim Image mit allen Dependencies (für lokales Bauen optional)
- **docker-compose.yml** - Orchestrierung mit vorgefertigtem Image
- **.dockerignore** - Excludes für optimierte Image-Größe

## 🚀 Quickstart

### Schritt 1: Repository klonen

```bash
git clone <repository-url>
cd discordBot
```

### Schritt 2: .env Datei erstellen

```bash
echo "TOKEN=your_discord_token_here" > .env
```

### Schritt 3: Bot starten

```bash
docker-compose -f Docker/docker-compose.yml up -d
```

Das war's! ✅ Der Bot läuft nun im Hintergrund.

---

## 📋 Alle Docker Commands

### Mit docker-compose (empfohlen):

```bash
# Bot starten
docker-compose -f Docker/docker-compose.yml up -d

# Logs anschauen
docker-compose -f Docker/docker-compose.yml logs -f

# Bot neustarten
docker-compose -f Docker/docker-compose.yml restart

# Bot stoppen
docker-compose -f Docker/docker-compose.yml down
```

### Mit docker run direkt:

```bash
# Image pullen
docker pull lxstOni/discord-bot:latest

# Container starten
docker run -d \
  --name discord-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/source/db:/app/source/db \
  lxstOni/discord-bot:latest

# Logs anschauen
docker logs -f discord-bot

# Container stoppen
docker stop discord-bot
```

---

## 🔧 Volumes

- `./logs` → `/app/logs` - Bot-Logs (persistent)
- `./data` → `/app/data` - Benutzerdefinierte Daten (persistent)
- `./source/db` → `/app/source/db` - Datenbank-Dateien (persistent)

---

## 🔐 Umgebungsvariablen

Die `.env` Datei wird automatisch geladen:

```env
TOKEN=your_discord_token_here
```

**Wichtig:** `.env` nicht ins Git committen! Sie ist in `.gitignore` eingetragen.

---

## 🛠 Lokales Image bauen (optional)

Falls du das Image selbst bauen möchtest:

```bash
docker build -f Docker/Dockerfile -t discord-bot:local .
docker run -d \
  --name discord-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/source/db:/app/source/db \
  discord-bot:local
```

---

Siehe auch: [Hauptdokumentation](../README.md#docker-installation)

