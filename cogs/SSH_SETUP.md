# SSH Setup Anleitung

Komplette Anleitung zum Einrichten von SSH für die Discord Bot Server-Steuerung.

## 📋 Voraussetzungen

- Linux/Unix Server mit SSH Zugang
- Root oder sudo Rechte auf dem Ziel-Server
- Discord Bot läuft auf einem Server (kann derselbe sein)

## 🔑 1. SSH Key Generieren

Auf dem Server wo der Bot läuft:

```bash
# SSH Key erstellen
ssh-keygen -t rsa -b 4096 -f ~/.ssh/discord_bot

# Keine Passphrase eingeben (einfach Enter drücken)
# Dies erstellt:
# - ~/.ssh/discord_bot (Private Key)
# - ~/.ssh/discord_bot.pub (Public Key)
```

**Wichtig:** Der Private Key darf NIEMALS geteilt oder in Git commitet werden!

## 📤 2. Public Key auf Ziel-Server installieren

### Methode 1: ssh-copy-id (Empfohlen)

```bash
ssh-copy-id -i ~/.ssh/discord_bot.pub admin@192.168.1.100
# Ersetzen Sie 'admin' und '192.168.1.100' mit Ihren Werten
# Beim ersten Mal wird nach dem Passwort gefragt
```

### Methode 2: Manuell

Auf dem **Ziel-Server**:

```bash
# In authorized_keys einfügen
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Public Key hinzufügen
echo "INHALT_DES_PUBLIC_KEYS" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Um den Public Key Inhalt zu bekommen (auf dem Bot-Server):
```bash
cat ~/.ssh/discord_bot.pub
```

## ✅ 3. Verbindung testen

```bash
# Test von Bot-Server zum Ziel-Server
ssh -i ~/.ssh/discord_bot admin@192.168.1.100

# Sollte OHNE Passwort funktionieren!
# Wenn Sie sich einloggen können → Erfolgreich!
```

## 🔐 4. Sudo Rechte konfigurieren (für poweroff/reboot)

Auf dem **Ziel-Server**:

```bash
# Sudoers bearbeiten
sudo visudo

# Folgende Zeilen AM ENDE hinzufügen:
# (Ersetzen Sie 'admin' mit Ihrem Benutzernamen)
```

```sudoers
# Discord Bot Berechtigungen
admin ALL=(ALL) NOPASSWD: /sbin/poweroff
admin ALL=(ALL) NOPASSWD: /sbin/reboot
admin ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart *
admin ALL=(ALL) NOPASSWD: /usr/bin/systemctl status *
admin ALL=(ALL) NOPASSWD: /usr/bin/systemctl start *
admin ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop *
```

**Testen:**
```bash
# Sollte NICHT nach Passwort fragen
sudo -n systemctl status ssh

# Wenn kein Passwort-Prompt → Erfolgreich!
```

## 🐳 5. Docker Rechte (optional)

Falls Sie Docker Compose verwenden möchten:

```bash
# User zur Docker-Gruppe hinzufügen
sudo usermod -aG docker admin

# Neuanmeldung erforderlich oder:
newgrp docker

# Test
docker ps
# Sollte ohne sudo funktionieren
```

## 🔒 6. SSH Server absichern

Auf dem **Ziel-Server** in `/etc/ssh/sshd_config`:

```bash
sudo nano /etc/ssh/sshd_config
```

Empfohlene Einstellungen:

```config
# Passwort-Authentifizierung deaktivieren
PasswordAuthentication no

# Root Login verbieten
PermitRootLogin no

# Nur Key-basierte Auth
PubkeyAuthentication yes

# Optional: Nur bestimmte User erlauben
AllowUsers admin

# Optional: SSH Port ändern (Security through obscurity)
Port 2222
```

SSH neu starten:
```bash
sudo systemctl restart sshd
```

⚠️ **WARNUNG:** Testen Sie die Verbindung in einem neuen Terminal bevor Sie das aktuelle schließen!

## 📁 7. Verzeichnisstruktur für Docker Compose

Empfohlene Struktur auf dem Ziel-Server:

```bash
# Erstellen Sie ein Hauptverzeichnis
mkdir -p /home/admin/docker
cd /home/admin/docker

# Projekt-Verzeichnisse
mkdir -p myapp backend frontend

# Beispiel: myapp
cd myapp
nano docker-compose.yml
```

Beispiel `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    restart: unless-stopped

  app:
    image: node:18-alpine
    working_dir: /app
    volumes:
      - ./app:/app
    restart: unless-stopped
```

## 🔥 8. Firewall konfigurieren (optional aber empfohlen)

```bash
# UFW installieren (falls nicht vorhanden)
sudo apt install ufw

# SSH erlauben (WICHTIG: Zuerst!)
sudo ufw allow 22/tcp  # Oder Ihr SSH Port

# Weitere Ports nach Bedarf
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Firewall aktivieren
sudo ufw enable

# Status prüfen
sudo ufw status
```

Für erweiterte Sicherheit - nur Bot-IP erlauben:
```bash
# SSH nur von Bot-Server IP
sudo ufw allow from 192.168.1.50 to any port 22 proto tcp
```

## 🛡️ 9. Fail2Ban installieren

Schutz vor Brute-Force Angriffen:

```bash
# Installation
sudo apt install fail2ban

# Konfiguration
sudo nano /etc/fail2ban/jail.local
```

```ini
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
```

```bash
# Starten
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Status
sudo fail2ban-client status sshd
```

## 📝 10. Bot Konfiguration

In Ihrer `.env` Datei:

```env
# Server Liste
SERVERS=homeserver

# Homeserver Konfiguration
SERVER_HOMESERVER_NAME=Homeserver
SERVER_HOMESERVER_HOST=192.168.1.100
SERVER_HOMESERVER_USER=admin
SERVER_HOMESERVER_KEY=/home/botuser/.ssh/discord_bot
SERVER_HOMESERVER_PORT=22
SERVER_HOMESERVER_EMOJI=🏠
```

## ✅ 11. Kompletter Test

```bash
# 1. SSH Key Test
ssh -i ~/.ssh/discord_bot admin@192.168.1.100 'echo SSH funktioniert'

# 2. Sudo Test
ssh -i ~/.ssh/discord_bot admin@192.168.1.100 'sudo -n systemctl status ssh'

# 3. Docker Test (falls verwendet)
ssh -i ~/.ssh/discord_bot admin@192.168.1.100 'docker ps'

# 4. Docker Compose Test
ssh -i ~/.ssh/discord_bot admin@192.168.1.100 'cd /home/admin/docker/myapp && docker compose ps'

# Alle sollten ohne Passwort-Prompt funktionieren!
```

## 🚀 12. Bot starten

```bash
cd /path/to/discordBot
python main.py
```

Test in Discord:
```
/list_servers
/ping_server server:homeserver
/server_status server:homeserver
```

## 🔧 Troubleshooting

### Problem: "Permission denied (publickey)"

**Lösung:**
```bash
# Prüfen Sie Berechtigungen
chmod 600 ~/.ssh/discord_bot
chmod 644 ~/.ssh/discord_bot.pub

# Auf Ziel-Server:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Problem: "Host key verification failed"

**Lösung:**
```bash
# Manuell verbinden einmal:
ssh -i ~/.ssh/discord_bot admin@192.168.1.100
# Tippen Sie "yes" wenn gefragt

# Oder:
ssh-keyscan -H 192.168.1.100 >> ~/.ssh/known_hosts
```

### Problem: Sudo fragt nach Passwort

**Lösung:**
```bash
# Testen Sie:
sudo -n poweroff

# Sollte nicht nach Passwort fragen
# Falls doch: sudoers nochmal prüfen
sudo visudo

# Stellen Sie sicher dass NOPASSWD NACH allen anderen Regeln steht!
```

### Problem: Docker Compose nicht gefunden

**Lösung:**
```bash
# Prüfen Sie Docker Compose Installation
docker compose version

# Falls nicht installiert:
sudo apt update
sudo apt install docker-compose-plugin

# Oder alte Version:
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Problem: Connection timeout

**Lösung:**
```bash
# Prüfen Sie ob SSH Server läuft
sudo systemctl status sshd

# Prüfen Sie Firewall
sudo ufw status

# Prüfen Sie ob Port offen ist
netstat -tuln | grep 22

# Von Bot-Server testen:
telnet 192.168.1.100 22
```

## 📚 Weiterführende Ressourcen

- [SSH Best Practices](https://www.ssh.com/academy/ssh/keygen)
- [Docker Documentation](https://docs.docker.com/)
- [UFW Guide](https://help.ubuntu.com/community/UFW)
- [Fail2Ban Documentation](https://www.fail2ban.org/)

## ⚠️ Sicherheits-Checkliste

- [ ] SSH Keys statt Passwörter verwenden
- [ ] PasswordAuthentication in sshd_config deaktiviert
- [ ] Private Key NIEMALS geteilt oder in Git
- [ ] Firewall konfiguriert
- [ ] Fail2Ban installiert
- [ ] Sudo auf notwendige Befehle beschränkt
- [ ] Bot nicht als root laufen
- [ ] SSH Port geändert (optional)
- [ ] Command Logging aktiviert
- [ ] Regelmäßige Updates
- [ ] Backups konfiguriert

---

✅ **Setup abgeschlossen!** Ihr Bot kann jetzt sicher Server steuern.
