# Server Control - Nutzungsdokumentation

Komplette Anleitung zur Verwendung der Discord Server-Steuerung.

## 📚 Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Verfügbare Befehle](#verfügbare-befehle)
3. [Detaillierte Befehlsbeschreibungen](#detaillierte-befehlsbeschreibungen)
4. [Beispiele](#beispiele)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## 🎯 Übersicht

Die Server-Steuerung ermöglicht es dem Bot Owner, Server sicher über Discord zu verwalten.

**Features:**
- ✅ SSH-basierte sichere Verbindung
- ✅ Moderne Discord UI (Slash Commands, Buttons, Select Menus)
- ✅ Server Management (poweroff, reboot, status)
- ✅ Docker Compose Integration
- ✅ Automatisches Monitoring
- ✅ Command Logging
- ✅ Nur für Bot Owner

## 🎮 Verfügbare Befehle

### Haupt-Befehle

| Befehl | Beschreibung | Parameter |
|--------|--------------|-----------|
| `/server_control` | Führt Server-Befehle aus | server, command, parameter |
| `/docker` | Docker Compose Befehle | server, command, project, options |
| `/server_status` | Zeigt Server-Status | server |
| `/list_servers` | Listet alle Server | - |
| `/ping_server` | Prüft Erreichbarkeit | server |

### Server Control Commands

| Command | Beschreibung | Bestätigung |
|---------|--------------|-------------|
| `poweroff` | Server herunterfahren | ✅ Ja |
| `reboot` | Server neu starten | ✅ Ja |
| `status` | Vollständiger Status | ❌ Nein |
| `uptime` | Server Laufzeit | ❌ Nein |
| `disk_usage` | Festplattennutzung | ❌ Nein |
| `memory_usage` | RAM Nutzung | ❌ Nein |
| `docker_ps` | Laufende Container | ❌ Nein |
| `docker_stats` | Container Ressourcen | ❌ Nein |

### Docker Compose Commands

| Command | Beschreibung | Bestätigung |
|---------|--------------|-------------|
| `up` | Container starten | ❌ Nein |
| `down` | Container stoppen | ✅ Ja |
| `restart` | Container neu starten | ❌ Nein |
| `logs` | Logs anzeigen (50 Zeilen) | ❌ Nein |
| `ps` | Container Status | ❌ Nein |
| `pull` | Images aktualisieren | ❌ Nein |

## 📖 Detaillierte Befehlsbeschreibungen

### `/server_control`

Führt vordefinierte Befehle auf einem Server aus.

**Parameter:**
- `server`: Wähle einen Server aus der konfigurierten Liste
- `command`: Befehl der ausgeführt werden soll
- `parameter`: Optional, für bestimmte Befehle

**Beispiel:**
```
/server_control server:homeserver command:poweroff
```

**Workflow bei kritischen Befehlen:**
1. Command eingeben
2. Bestätigungsdialog erscheint
3. Klicke "✅ Ja, ausführen" oder "❌ Abbrechen"
4. Bei Ja: Befehl wird ausgeführt
5. Status-Update wird angezeigt
6. Bei poweroff/reboot: Automatisches Monitoring

**Response:**
- ✅ Erfolgreich: Grüner Embed mit Output
- ❌ Fehler: Roter Embed mit Fehlermeldung
- 🔍 Monitoring: Status-Updates alle 5 Sekunden

---

### `/docker`

Steuert Docker Compose Projekte auf einem Server.

**Parameter:**
- `server`: Ziel-Server
- `command`: Docker Compose Befehl (up, down, restart, logs, ps, pull)
- `project`: Projekt-Name (Ordnername in DOCKER_COMPOSE_PATH)
- `options`: Optional, zusätzliche Flags (z.B. `--build`)

**Beispiel:**
```
/docker server:homeserver command:up project:myapp
/docker server:homeserver command:up project:myapp options:--build
/docker server:homeserver command:logs project:myapp
```

**Workflow:**
1. Command eingeben
2. Bei `down`: Bestätigungsdialog
3. Status-Nachricht "🚀 Starte Container..."
4. Befehl wird ausgeführt
5. Container-Status wird angezeigt
6. Action-Buttons verfügbar

**Response Features:**
- Container-Liste nach up/restart/ps
- Logs-Ausgabe (letzte 50 Zeilen)
- Status jedes Containers
- Interaktive Buttons: [📊 Status] [🔄 Ping]

---

### `/server_status`

Zeigt umfassenden Server-Status mit Echtzeit-Daten.

**Parameter:**
- `server`: Server zur Abfrage

**Beispiel:**
```
/server_status server:homeserver
```

**Angezeigte Informationen:**
- 🟢/🔴 Online/Offline Status
- 🏠 Host & Port
- ⏱️ Uptime (z.B. "up 3 days, 5 hours")
- 🧠 Memory (z.B. "2.1GB / 8GB (26%)")
- 💾 Disk (z.B. "45GB / 100GB (45%)")
- 💻 CPU Usage (z.B. "23.5%")
- 🐳 Docker Container Anzahl

**Response Zeit:**
- Typisch: 2-5 Sekunden
- Abhängig von Server-Antwortzeit

---

### `/list_servers`

Zeigt alle konfigurierten Server mit Status-Übersicht.

**Parameter:** Keine

**Beispiel:**
```
/list_servers
```

**Angezeigt:**
- Server-Name mit Emoji
- Host-Adresse
- 🟢/🔴 Online/Offline Status

**Nützlich für:**
- Übersicht aller Server
- Schnelle Status-Prüfung
- Server-Namen für andere Befehle

---

### `/ping_server`

Prüft ob ein Server erreichbar ist (SSH-Verbindungstest).

**Parameter:**
- `server`: Server zum Pingen

**Beispiel:**
```
/ping_server server:homeserver
```

**Response:**
- 🟢 Online: Server antwortet auf SSH
- 🔴 Offline: Keine Verbindung möglich
- Timeout: 5 Sekunden

**Unterschied zu `/server_status`:**
- Ping: Nur Verbindungstest
- Status: Vollständige System-Informationen

---

## 💡 Beispiele

### Beispiel 1: Server herunterfahren

```
1. Command: /server_control server:homeserver command:poweroff

2. Bot zeigt:
   ┌─────────────────────────────────────┐
   │ ⚠️ Bestätigung erforderlich         │
   ├─────────────────────────────────────┤
   │ Server: 🏠 Homeserver               │
   │ Befehl: sudo poweroff               │
   │                                     │
   │ Bist du sicher?                    │
   │ [✅ Ja, ausführen] [❌ Abbrechen]  │
   └─────────────────────────────────────┘

3. Klick auf [✅ Ja, ausführen]

4. Bot zeigt:
   🔄 Führe Befehl aus...

5. Nach Ausführung:
   ┌─────────────────────────────────────┐
   │ ✅ Befehl erfolgreich ausgeführt    │
   ├─────────────────────────────────────┤
   │ Server: 🏠 Homeserver               │
   │ Befehl: poweroff                    │
   │ 🔍 Monitoring: Wird überwacht...    │
   └─────────────────────────────────────┘

6. Nach ~30 Sekunden:
   ┌─────────────────────────────────────┐
   │ ✅ Server 'Homeserver' wurde        │
   │    heruntergefahren                 │
   ├─────────────────────────────────────┤
   │ Status: 🔴 Offline                  │
   │ Zeitpunkt: 14:35:22                │
   └─────────────────────────────────────┘
```

### Beispiel 2: Docker Compose Up mit Build

```
1. Command: /docker server:homeserver command:up project:myapp options:--build

2. Bot zeigt:
   🚀 Starte Container...

3. Nach Ausführung:
   ┌─────────────────────────────────────┐
   │ ✅ Docker Compose UP erfolgreich    │
   ├─────────────────────────────────────┤
   │ 📦 Projekt: myapp                   │
   │ 🖥️ Server: 🏠 Homeserver            │
   │                                     │
   │ Output:                             │
   │ ┌─────────────────────────────────┐ │
   │ │ [+] Building 45.2s              │ │
   │ │ [+] Running 3/3                 │ │
   │ │ ✔ Container myapp-web-1  Up 3s  │ │
   │ │ ✔ Container myapp-db-1   Up 3s  │ │
   │ │ ✔ Container myapp-app-1  Up 2s  │ │
   │ └─────────────────────────────────┘ │
   │                                     │
   │ 🐳 Container Status:                │
   │ ┌─────────────────────────────────┐ │
   │ │ NAME         STATUS             │ │
   │ │ myapp-web-1  Up 3 seconds       │ │
   │ │ myapp-db-1   Up 3 seconds       │ │
   │ │ myapp-app-1  Up 2 seconds       │ │
   │ └─────────────────────────────────┘ │
   │                                     │
   │ [📊 Status] [🔄 Ping]              │
   └─────────────────────────────────────┘
```

### Beispiel 3: Server Status abfragen

```
1. Command: /server_status server:homeserver

2. Bot zeigt:
   ┌─────────────────────────────────────┐
   │ 🏠 Server Status: Homeserver        │
   ├─────────────────────────────────────┤
   │ Status: 🟢 Online                   │
   │ Host: 192.168.1.100                │
   │ Port: 22                           │
   │                                     │
   │ ⏱️ Uptime:                          │
   │ up 3 days, 5 hours, 23 minutes     │
   │                                     │
   │ 🧠 Memory:                          │
   │ 2.1GB / 8GB (26%)                  │
   │                                     │
   │ 💾 Disk:                            │
   │ 45GB / 100GB (45%)                 │
   │                                     │
   │ 💻 CPU Usage:                       │
   │ 23.5%                              │
   │                                     │
   │ 🐳 Docker Container:                │
   │ 5                                  │
   └─────────────────────────────────────┘
```

### Beispiel 4: Docker Logs anzeigen

```
1. Command: /docker server:homeserver command:logs project:myapp

2. Bot zeigt:
   ┌─────────────────────────────────────┐
   │ ✅ Docker Compose LOGS erfolgreich  │
   ├─────────────────────────────────────┤
   │ 📦 Projekt: myapp                   │
   │ 🖥️ Server: 🏠 Homeserver            │
   │                                     │
   │ Output:                             │
   │ ┌─────────────────────────────────┐ │
   │ │ myapp-web-1  | Server started   │ │
   │ │ myapp-web-1  | Listening on 80  │ │
   │ │ myapp-db-1   | Database ready   │ │
   │ │ myapp-app-1  | App initialized  │ │
   │ │ myapp-app-1  | Connected to DB  │ │
   │ │ ...                             │ │
   │ └─────────────────────────────────┘ │
   └─────────────────────────────────────┘
```

## 🎯 Best Practices

### Sicherheit

1. **Niemals in öffentlichen Channels verwenden**
   - Commands sind nur für Bot Owner sichtbar
   - Verwenden Sie trotzdem ephemeral Messages

2. **Command Logging aktivieren**
   ```env
   COMMAND_LOG_CHANNEL_ID=123456789
   ```
   - Erstellen Sie einen privaten Log-Channel
   - Überwachen Sie regelmäßig

3. **Minimale Berechtigungen**
   - Geben Sie nur notwendige sudo-Rechte
   - Verwenden Sie dedizierte Bot-User

### Server Management

1. **Vor poweroff prüfen**
   - Prüfen Sie `/server_status` vor dem Herunterfahren
   - Stellen Sie sicher dass keine kritischen Tasks laufen

2. **Docker Compose Best Practices**
   ```bash
   # Logs vor Restart prüfen
   /docker command:logs project:myapp
   
   # Dann erst Restart
   /docker command:restart project:myapp
   ```

3. **Monitoring nutzen**
   - Nach reboot: Warten Sie auf "Server ist wieder online"
   - Prüfen Sie Status mit `/server_status`

### Performance

1. **Timeout beachten**
   - Commands haben 30-120 Sekunden Timeout
   - Bei langen Builds: Verwenden Sie Build außerhalb

2. **Rate Limiting**
   - Führen Sie nicht zu viele Commands gleichzeitig aus
   - Bei poweroff/reboot: Warten Sie auf Abschluss

## 🔧 Troubleshooting

### "❌ Server nicht gefunden"

**Ursache:** Server nicht in .env konfiguriert

**Lösung:**
```bash
# .env prüfen
cat .env | grep SERVER_

# Sollte zeigen:
# SERVERS=homeserver,webserver
# SERVER_HOMESERVER_NAME=...
```

### "SSH Authentifizierung fehlgeschlagen"

**Ursache:** SSH Key Problem

**Lösung:**
```bash
# Test Connection
ssh -i /path/to/key user@host

# Berechtigungen prüfen
chmod 600 /path/to/key

# Auf Ziel-Server:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### "Permission denied" bei sudo

**Ursache:** Sudo Konfiguration fehlt

**Lösung:**
```bash
# Auf Ziel-Server
sudo visudo

# Hinzufügen:
admin ALL=(ALL) NOPASSWD: /sbin/poweroff
admin ALL=(ALL) NOPASSWD: /sbin/reboot

# Testen:
sudo -n poweroff
# Sollte NICHT nach Passwort fragen
```

### "Connection timeout"

**Ursachen:**
- Server ist offline
- Firewall blockiert
- Falsche IP/Port

**Lösung:**
```bash
# Ping prüfen
ping 192.168.1.100

# Port prüfen
telnet 192.168.1.100 22

# SSH prüfen
ssh -v -i /path/to/key user@host
```

### Docker Compose nicht gefunden

**Ursache:** Projekt-Pfad falsch

**Lösung:**
```bash
# In .env prüfen
DOCKER_COMPOSE_PATH=/home/admin/docker

# Auf Server prüfen
ls -la /home/admin/docker/
# Sollte Ihre Projekte zeigen

# Projekt prüfen
ls -la /home/admin/docker/myapp/
# Sollte docker-compose.yml enthalten
```

### "Bot Owner Only" Error

**Ursache:** Sie sind nicht der Bot Owner

**Lösung:**
- Nur der Owner der Discord Application kann diese Befehle nutzen
- Prüfen Sie in Discord Developer Portal
- Sie müssen die Application besitzen

## 📊 Command Logging

Alle Befehle werden (wenn konfiguriert) in einem Log-Channel protokolliert:

```
┌─────────────────────────────────────┐
│ 📋 Server Command Log              │
├─────────────────────────────────────┤
│ User: @YourName (123456789)        │
│ Server: Homeserver                 │
│ Command:                           │
│ ┌─────────────────────────────────┐ │
│ │ sudo poweroff                   │ │
│ └─────────────────────────────────┘ │
│ Status: ✅ Erfolg                   │
│ Zeitpunkt: 18.12.2025 14:35:22    │
└─────────────────────────────────────┘
```

## 🔄 Workflow-Diagramme

### Poweroff Workflow

```
User gibt Command ein
    ↓
Bestätigungs-Dialog
    ↓
[Ja] ← User → [Abbrechen]
    ↓                ↓
Befehl wird    Abgebrochen
ausgeführt
    ↓
"Befehl gesendet"
    ↓
Monitoring startet
    ↓
Ping alle 5 Sek
    ↓
Server offline?
    ↓
"Server heruntergefahren"
```

### Docker Up Workflow

```
User gibt Command ein
    ↓
"Starte Container..."
    ↓
docker compose up -d
    ↓
Erfolgreich?
    ↓              ↓
  Ja              Nein
    ↓              ↓
Container      Fehler-
Status         meldung
anzeigen
    ↓
Action Buttons
```

---

## 📝 Zusammenfassung

✅ **Wichtigste Befehle:**
- `/server_status` - Status prüfen
- `/server_control` - Server steuern
- `/docker` - Container verwalten

✅ **Sicherheit:**
- Nur Bot Owner
- SSH Keys
- Command Logging
- Bestätigungen

✅ **Support:**
- Siehe [SSH_SETUP.md](SSH_SETUP.md) für Setup
- Siehe [.env.example](.env.example) für Konfiguration

🚀 **Viel Erfolg mit der Server-Steuerung!**
